const socket = io();

// Optional: auto-log socket events
socket.on('connect', () => console.log('[SocketIO] Connected'));
socket.on('disconnect', () => console.log('[SocketIO] Disconnected'));
