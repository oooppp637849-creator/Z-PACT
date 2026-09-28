// chat_notif.js - Floating Chat & Notifications Engine
// Ultra-fast, zero-bandwidth cache, hardcore security hardened

let chatWs = null;
let currentReplyToId = null;
let chatMessagesCache = [];
const CHAT_CACHE_KEY = "zpact_chat_messages_v1";

window.handleAvatarError = (imgElement) => {
    imgElement.src = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' fill='none'><circle cx='50' cy='50' r='50' fill='%231e293b'/><path d='M50 30a12 12 0 100 24 12 12 0 000-24zM25 78c0-12 12-16 25-16s25 4 25 16' stroke='%2338bdf8' stroke-width='4' stroke-linecap='round'/></svg>`;
    imgElement.onerror = null;
};

// Safe string escaping for HTML
function escapeHTML(str) {
    if (!str) return '';
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

async function initChatAndNotifications() {
    const pathname = window.location.pathname.toLowerCase();
    const isSettingsPage = pathname.includes('settings');

    // 1. Inject Chat Widget if applicable (NEVER on settings page as requested)
    if (!isSettingsPage) {
        injectChatWidget();
    }

    const token = localStorage.getItem("access_token");
    if (!token) return;

    // 2. Load Notifications in background (Never blocks chat)
    loadNotificationsAsync();

    // 3. Initialize Chat WebSocket & load messages (skip if settings page)
    if (isSettingsPage || !document.getElementById("chat-window")) return;

    // Connect WebSocket
    connectChatWs();

    // Load messages (Instant from cache, then sync with server)
    loadHistoricalMessages();
}

// -------------------------------------------------------------
// Notifications Loading (Isolated & Non-blocking)
// -------------------------------------------------------------
async function loadNotificationsAsync() {
    try {
        if (!window.usersAPI || typeof window.usersAPI.getNotifications !== "function") return;
        const notifs = await window.usersAPI.getNotifications();
        if (!Array.isArray(notifs)) return;

        const unreadCount = notifs.filter(n => !n.is_read).length;
        
        const badge = document.getElementById("notif-badge");
        if (badge) {
            badge.textContent = unreadCount;
            badge.style.display = unreadCount > 0 ? "flex" : "none";
        }
        
        const list = document.getElementById("notif-list");
        if (list) {
            if (notifs.length === 0) {
                list.innerHTML = `<div style="padding:1rem;text-align:center;color:var(--text-muted)">لا توجد إشعارات</div>`;
            } else {
                list.innerHTML = notifs.map(n => `
                    <div class="notif-item ${!n.is_read ? 'unread' : ''}">
                        <div style="font-weight:bold;font-size:13px">${escapeHTML(n.title)}</div>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:4px">${escapeHTML(n.message)}</div>
                    </div>
                `).join('');
            }
        }
    } catch (e) {
        // Silently handle notification errors without impacting chat
    }
}

// -------------------------------------------------------------
// Chat History Loading (Instant 0ms Cache + Server Reconciliation)
// -------------------------------------------------------------
async function loadHistoricalMessages() {
    const msgsContainer = document.getElementById("chat-messages-container");
    if (!msgsContainer) return;

    // A. Instant Local Render from Session Cache (0ms latency, zero data consumption)
    try {
        const cachedRaw = sessionStorage.getItem(CHAT_CACHE_KEY);
        if (cachedRaw) {
            const cachedList = JSON.parse(cachedRaw);
            if (Array.isArray(cachedList) && cachedList.length > 0) {
                chatMessagesCache = cachedList;
                msgsContainer.innerHTML = "";
                cachedList.forEach(msg => appendChatMessage(msg, false));
                scrollToChatBottom();
            }
        }
    } catch (e) {
        // Ignore cache parse error
    }

    // B. Fetch fresh batch from server
    try {
        if (!window.chatAPI || typeof window.chatAPI.getMessages !== "function") return;
        const msgs = await window.chatAPI.getMessages();
        if (Array.isArray(msgs)) {
            chatMessagesCache = msgs;
            try {
                sessionStorage.setItem(CHAT_CACHE_KEY, JSON.stringify(msgs.slice(-50)));
            } catch (e) {}

            msgsContainer.innerHTML = "";
            msgs.forEach(msg => appendChatMessage(msg, false));
            scrollToChatBottom();
        }
    } catch (e) {
        console.warn("Failed to sync chat messages with server:", e);
    }
}

let chatReconnectTimer = null;

function connectChatWs() {
    const token = localStorage.getItem("access_token");
    if (!token || !window.chatAPI) return;
    if (chatWs && (chatWs.readyState === WebSocket.OPEN || chatWs.readyState === WebSocket.CONNECTING)) {
        return;
    }

    try {
        const wsUrl = `${window.chatAPI.getWsUrl()}?token=${token}`;
        chatWs = new WebSocket(wsUrl);

        chatWs.onopen = () => {
            updateChatStatus("متصل", "#10b981", "rgba(16, 185, 129, 0.15)");
            if (chatReconnectTimer) {
                clearTimeout(chatReconnectTimer);
                chatReconnectTimer = null;
            }
        };

        chatWs.onclose = () => {
            updateChatStatus("جاري الاتصال...", "#f59e0b", "rgba(245, 158, 11, 0.15)");
            if (!chatReconnectTimer) {
                chatReconnectTimer = setTimeout(() => {
                    chatReconnectTimer = null;
                    connectChatWs();
                }, 3000);
            }
        };

        chatWs.onerror = () => {
            updateChatStatus("غير متصل", "#ef4444", "rgba(239, 68, 68, 0.15)");
        };

        chatWs.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.action === "delete_message") {
                    const el = document.getElementById(`chat-msg-${msg.message_id}`);
                    if (el) el.remove();
                    chatMessagesCache = chatMessagesCache.filter(m => m.id !== msg.message_id);
                    try {
                        sessionStorage.setItem(CHAT_CACHE_KEY, JSON.stringify(chatMessagesCache.slice(-50)));
                    } catch (e) {}
                } else if (msg.action === "job_update") {
                    if (window.jobManager && typeof window.jobManager.handleWsUpdate === "function") {
                        window.jobManager.handleWsUpdate(msg);
                    }
                } else if (msg.action === "error") {
                    if (window.showToast) {
                        window.showToast(msg.message, "error");
                    } else {
                        alert(msg.message);
                    }
                } else if (msg.action === "new_message" || msg.id) {
                    appendChatMessage(msg, true);
                    // Update cache
                    if (!chatMessagesCache.some(m => m.id === msg.id)) {
                        chatMessagesCache.push(msg);
                        try {
                            sessionStorage.setItem(CHAT_CACHE_KEY, JSON.stringify(chatMessagesCache.slice(-50)));
                        } catch (e) {}
                    }
                }
            } catch (e) {
                console.error("Chat message parse error", e);
            }
        };
    } catch (e) {
        console.error("WebSocket connection error:", e);
    }
}

function updateChatStatus(text, color, bg) {
    const statusEl = document.getElementById("chat-status-indicator");
    if (statusEl) {
        statusEl.textContent = text;
        statusEl.style.color = color;
        statusEl.style.background = bg || "transparent";
    }
}

function ensureChatConnected() {
    connectChatWs();
}

function toggleNotifDropdown() {
    const dropdown = document.getElementById("notif-dropdown");
    if (!dropdown) return;
    dropdown.classList.toggle("show");
    
    if (dropdown.classList.contains("show")) {
        window.usersAPI.markNotificationsRead().then(() => {
            const badge = document.getElementById("notif-badge");
            if (badge) badge.style.display = "none";
        }).catch(e => console.error(e));
    }
}

function toggleChat() {
    const w = document.getElementById("chat-window");
    const widget = document.getElementById("chat-widget");
    if (!w) return;
    
    // Ensure widget is visible if user toggles it
    if (widget && widget.style.display === "none") {
        widget.style.display = "";
    }

    const isOpen = w.classList.toggle("show");
    if (widget) {
        widget.classList.toggle("chat-open", isOpen);
    }
    
    const bottomNav = document.getElementById("mobile-bottom-nav") || document.querySelector(".bottom-nav");
    if (isOpen) {
        document.body.classList.add("chat-open-scroll-lock");
        if (bottomNav) bottomNav.style.display = "none";
        ensureChatConnected();
        
        // If message list is currently empty, trigger instant load
        const container = document.getElementById("chat-messages-container");
        if (container && container.children.length === 0) {
            loadHistoricalMessages();
        }
        
        setTimeout(() => {
            scrollToChatBottom();
            const inp = document.getElementById("chat-input");
            if (inp && window.innerWidth > 768) inp.focus();
        }, 120);
    } else {
        document.body.classList.remove("chat-open-scroll-lock");
        if (bottomNav) bottomNav.style.display = "";
        cancelReply();
    }
}

// -------------------------------------------------------------
// Message Rendering (XSS Immune & DOM Safe)
// -------------------------------------------------------------
function appendChatMessage(msg, shouldScroll = true) {
    const container = document.getElementById("chat-messages-container");
    if (!container || !msg || !msg.id) return;
    
    // Prevent duplicate messages in DOM
    const existing = document.getElementById(`chat-msg-${msg.id}`);
    if (existing) return;
    
    const currentUser = window.getCurrentUser();
    const isMe = currentUser && Number(currentUser.id) === Number(msg.user_id);
    
    // Resolve user name cleanly
    let name = "مستخدم";
    if (isMe) {
        name = currentUser.full_name || "أنا";
    } else if (msg.user_name) {
        name = msg.user_name;
    } else if (msg.user && msg.user.full_name) {
        name = msg.user.full_name;
    }
    
    // Resolve avatar URL cleanly
    let avatarPath = "";
    if (isMe && currentUser.profile_picture_path) {
        avatarPath = currentUser.profile_picture_path;
    } else if (msg.avatar) {
        avatarPath = msg.avatar;
    } else if (msg.user && msg.user.profile_picture_path) {
        avatarPath = msg.user.profile_picture_path;
    }
    
    const defaultAvatarSvg = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' fill='none'><circle cx='50' cy='50' r='50' fill='%231e293b'/><path d='M50 30a12 12 0 100 24 12 12 0 000-24zM25 78c0-12 12-16 25-16s25 4 25 16' stroke='%2338bdf8' stroke-width='4' stroke-linecap='round'/></svg>`;
    const avatarUrl = avatarPath ? `/${avatarPath.replace(/^\/+/, '')}` : defaultAvatarSvg;
    
    let timeStr = '';
    if (msg.created_at) {
        try {
            timeStr = new Date(msg.created_at).toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' });
        } catch (e) {
            timeStr = '';
        }
    }
    
    const div = document.createElement("div");
    div.id = `chat-msg-${msg.id}`;
    div.style.display = "flex";
    div.style.flexDirection = isMe ? "row-reverse" : "row";
    div.style.gap = "10px";
    div.style.alignItems = "flex-start";
    div.style.maxWidth = "85%";
    div.style.width = "100%";
    div.style.marginBottom = "12px";
    div.style.alignSelf = isMe ? "flex-end" : "flex-start";
    
    // Construct HTML with strict escaping
    let replyHtml = '';
    if (msg.reply_preview) {
        const replyHeader = msg.reply_user_name ? `<strong style="display:block; margin-bottom: 2px; color: var(--primary);">الرد على ${escapeHTML(msg.reply_user_name)}:</strong>` : '';
        const previewText = msg.reply_preview.length > 50 ? msg.reply_preview.substring(0, 50) + '...' : msg.reply_preview;
        replyHtml = `
            <div style="background: rgba(0,0,0,0.18); border-right: 3px solid var(--primary); padding: 6px 8px; margin-bottom: 6px; border-radius: 4px; font-size: 11px; opacity: 0.85; word-break: break-word; text-align: right; direction: rtl;">
                ${replyHeader}
                <span>${escapeHTML(previewText)}</span>
            </div>
        `;
    }
    
    div.innerHTML = `
        <img src="${avatarUrl}" style="width: 32px; height: 32px; min-width: 32px; min-height: 32px; aspect-ratio: 1 / 1; border-radius: 50%; border: 1.5px solid ${isMe ? 'var(--primary)' : 'var(--secondary)'}; object-fit: cover; flex-shrink: 0; box-shadow: 0 2px 8px rgba(0,0,0,0.3);" onerror="window.handleAvatarError(this)">
        <div style="display: flex; flex-direction: column; align-items: ${isMe ? 'flex-end' : 'flex-start'}; flex: 1; min-width: 0;">
            <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 3px; direction: rtl;">
                <span style="font-size: 11px; font-weight: 700; color: ${isMe ? 'var(--primary)' : 'var(--text-secondary)'}; white-space: nowrap;">${escapeHTML(name)}</span>
                <span style="font-size: 9px; color: var(--text-muted);">${timeStr}</span>
            </div>
            <div class="chat-bubble-content" style="background: ${isMe ? 'linear-gradient(135deg, var(--primary), var(--secondary))' : 'rgba(255,255,255,0.08)'}; color: #fff; padding: 10px 14px; border-radius: 14px; border-${isMe ? 'top-right' : 'top-left'}-radius: 0; font-size: 13px; line-height: 1.5; word-break: break-word; box-shadow: ${isMe ? '0 4px 12px var(--primary-glow)' : '0 2px 6px rgba(0,0,0,0.15)'}; border: 1px solid ${isMe ? 'transparent' : 'var(--border)'}; width: fit-content; max-width: 100%; position: relative;">
                ${replyHtml}
                <div class="chat-text-payload" style="white-space: pre-wrap;">${escapeHTML(msg.message)}</div>
                <div class="chat-bubble-actions" style="display: flex; gap: 8px; margin-top: 6px; justify-content: ${isMe ? 'flex-start' : 'flex-end'};">
                    <button class="chat-reply-action-btn" type="button" style="background: none; border: none; color: ${isMe ? 'rgba(255,255,255,0.7)' : 'var(--text-muted)'}; cursor: pointer; font-size: 12px; padding: 2px 4px;" title="رد">↩️</button>
                    ${(isMe || (window.isAdmin && window.isAdmin())) ? `<button class="chat-delete-action-btn" type="button" style="background: none; border: none; color: ${isMe ? 'rgba(255,255,255,0.7)' : 'var(--text-muted)'}; cursor: pointer; font-size: 12px; padding: 2px 4px;" title="حذف">🗑️</button>` : ''}
                </div>
            </div>
        </div>
    `;
    
    // Attach pure JS event listeners (Immune to quotes/XSS)
    const replyBtn = div.querySelector('.chat-reply-action-btn');
    if (replyBtn) {
        replyBtn.addEventListener('click', () => prepareReply(msg.id, msg.message));
    }
    
    const delBtn = div.querySelector('.chat-delete-action-btn');
    if (delBtn) {
        delBtn.addEventListener('click', () => deleteChatMessage(msg.id));
    }
    
    container.appendChild(div);
    if (shouldScroll) {
        scrollToChatBottom();
    }
}

function scrollToChatBottom() {
    const container = document.getElementById("chat-messages-container");
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

function sendChatMessage(e) {
    if (e && e.key && e.key !== "Enter") return;
    const input = document.getElementById("chat-input");
    if (!input) return;
    const val = input.value.trim();
    if (!val) return;
    
    if (val.length > 1000) {
        alert("الرسالة طويلة جداً (الحد الأقصى 1000 حرف).");
        return;
    }
    
    if (!chatWs || chatWs.readyState !== WebSocket.OPEN) {
        ensureChatConnected();
        setTimeout(() => {
            if (chatWs && chatWs.readyState === WebSocket.OPEN) {
                const payload = {
                    action: "send",
                    message: val,
                    reply_to_id: currentReplyToId
                };
                chatWs.send(JSON.stringify(payload));
                input.value = "";
                cancelReply();
            } else {
                alert("جاري إعادة الاتصال بالشات، يرجى المحاولة بعد لحظات...");
            }
        }, 500);
        return;
    }
    
    const payload = {
        action: "send",
        message: val,
        reply_to_id: currentReplyToId
    };
    
    chatWs.send(JSON.stringify(payload));
    input.value = "";
    cancelReply();
    if (window.innerWidth <= 768) {
        input.focus();
    }
}

function prepareReply(msgId, msgText) {
    currentReplyToId = msgId;
    const preview = document.getElementById("chat-reply-preview");
    const previewText = document.getElementById("chat-reply-text");
    if (preview && previewText) {
        previewText.textContent = msgText.length > 50 ? msgText.substring(0, 50) + '...' : msgText;
        preview.style.display = "block";
    }
    const input = document.getElementById("chat-input");
    if (input) input.focus();
}

function cancelReply() {
    currentReplyToId = null;
    const preview = document.getElementById("chat-reply-preview");
    if (preview) preview.style.display = "none";
}

async function deleteChatMessage(msgId) {
    if (!confirm("هل أنت متأكد من حذف هذه الرسالة؟")) return;
    try {
        await window.apiCall("DELETE", `/chat/messages/${msgId}`);
    } catch (e) {
        console.error("Delete failed", e);
    }
}

function injectChatWidget() {
    const pathname = window.location.pathname.toLowerCase();
    // Exclude settings page completely: user requested NO chat/support on settings
    if (pathname.includes('settings')) return;

    // Inject on store, admin, purchases, or preview pages
    const isAllowedPage = pathname.includes('store') || pathname.includes('admin') || pathname.includes('purchases') || pathname === '/' || pathname === '';
    if (!isAllowedPage) return;

    if (document.getElementById("chat-window")) return; // already injected

    const html = `
    <div class="chat-widget" id="chat-widget">
        <div id="chat-window" class="chat-window" role="dialog" aria-label="الشات العالمي">
            <div class="chat-header">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-weight: 700; color: var(--primary); font-size: 15px;">الشات العالمي</span>
                    <span id="chat-status-indicator" style="font-size: 11px; padding: 2px 8px; border-radius: 12px; background: rgba(16,185,129,0.15); color: #10b981;">متصل</span>
                </div>
                <button class="chat-close-btn" onclick="toggleChat()" aria-label="إغلاق الشات" title="إغلاق">✕</button>
            </div>
            <div id="chat-messages-container" class="chat-messages">
                <!-- Messages rendered here -->
            </div>
            <div class="chat-input-area">
                <div id="chat-reply-preview" style="display: none; background: rgba(0,242,255,0.1); border-right: 3px solid var(--primary); padding: 8px 12px; margin-bottom: 8px; border-radius: 6px; font-size: 12px; color: var(--text-secondary); position: relative; text-align: right;">
                    <span id="chat-reply-text"></span>
                    <button onclick="cancelReply()" style="position: absolute; left: 5px; top: 5px; background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 16px; padding: 4px;">✕</button>
                </div>
                <div>
                    <input type="text" id="chat-input" class="chat-input" placeholder="اكتب رسالة..." enterkeyhint="send" autocomplete="off" onkeydown="if(event.key==='Enter') sendChatMessage(event)">
                    <button class="btn btn-primary chat-send-btn" onclick="sendChatMessage()">إرسال</button>
                </div>
            </div>
        </div>
        <div class="chat-btn" id="chat-toggle-btn" onclick="toggleChat()" aria-label="فتح الشات" title="فتح الشات">
            💬
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', html);
    
    // Respect global preferences if set
    if (window.USER_PREFS && window.USER_PREFS.chat_visible === false) {
        document.getElementById("chat-widget").style.display = "none";
    }

    // Adapt to mobile visual viewport when virtual keyboard opens
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', () => {
            const chatWin = document.getElementById("chat-window");
            if (chatWin && chatWin.classList.contains("show") && window.innerWidth <= 768) {
                chatWin.style.height = `${window.visualViewport.height}px`;
                chatWin.style.top = `${window.visualViewport.offsetTop}px`;
                scrollToChatBottom();
            }
        });
    }
}

// Auto-reconnect when user returns to tab or unlocks phone
document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
        ensureChatConnected();
    }
});
window.addEventListener("focus", () => {
    ensureChatConnected();
});

// Ensure apiCall helper exists (supports both (method, endpoint) and (endpoint, options) patterns)
window.apiCall = async function(arg1, arg2) {
    const token = localStorage.getItem("access_token");
    let method = "GET";
    let endpoint = "";
    let body = undefined;
    let customHeaders = {};

    if (typeof arg1 === "string" && typeof arg2 === "object" && arg2 !== null && ("method" in arg2 || "body" in arg2)) {
        endpoint = arg1;
        method = arg2.method || "POST";
        body = arg2.body;
        if (arg2.headers) customHeaders = arg2.headers;
    } else {
        method = arg1;
        endpoint = arg2 || "";
    }

    let url = endpoint;
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
        if (url.startsWith("/api/")) {
            url = window.BASE_URL + url.substring(4);
        } else if (url.startsWith("/")) {
            url = window.BASE_URL + url;
        } else {
            url = window.BASE_URL + "/" + url;
        }
    }

    const headers = { ...customHeaders };
    if (token && !headers["Authorization"]) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const fetchConfig = { method, headers };
    if (body !== undefined) {
        fetchConfig.body = body;
    }

    const res = await fetch(url, fetchConfig);
    if (!res.ok) {
        const errData = await res.json().catch(() => null);
        const errorMsg = errData?.detail || `خطأ في الاتصال (${res.status})`;
        throw new Error(errorMsg);
    }
    return res.json();
};

// Global exports
window.toggleNotifDropdown = toggleNotifDropdown;
window.toggleChat = toggleChat;
window.sendChatMessage = sendChatMessage;
window.prepareReply = prepareReply;
window.cancelReply = cancelReply;
window.deleteChatMessage = deleteChatMessage;
window.loadHistoricalMessages = loadHistoricalMessages;

// Robust self-initialization (handles both pre- and post-DOMContentLoaded states)
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        if (window.isLoggedIn && window.isLoggedIn()) {
            initChatAndNotifications();
        }
    });
} else {
    if (window.isLoggedIn && window.isLoggedIn()) {
        initChatAndNotifications();
    }
}
