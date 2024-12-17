const express = require('express');
const http = require('http');
const https = require('https');
const fs = require('fs');
const { v4: uuid } = require('uuid');
const socketIO = require('socket.io');
const app = express();
const expressHTTPServer = http.createServer(app);

const options = {
    key: fs.readFileSync('server.key'),
    cert: fs.readFileSync('server.cert')
};
const expressHTTPSServer = https.createServer(options, app);
const io = new socketIO.Server(expressHTTPSServer);

let roomUsers = new Map();

app.use(express.static('public'));
app.set('view engine', 'ejs');

const port = 2037;
const baseIP = '192.168.1.6'; // Gantilah dengan alamat IP server yang benar
const baseURL = `https://${baseIP}:${port}/`; // Gunakan HTTPS untuk URL dasar

app.get('/', (req, res) => {
    const roomId = uuid();
    const roomLink = `${baseURL}${roomId}`;
    console.log(`Server running at: ${baseURL}`);
    console.log(`Generated new room link: ${roomLink}`);
    res.redirect(`/${roomId}`);
});

app.get("/:roomId", (req, res) => {
    const roomId = req.params.roomId;
    const roomLink = `${baseURL}${roomId}`;
    console.log(`Accessed room: ${roomLink}`);
    res.render('index', { roomId });
});

io.on('connection', (socket) => {
    console.log(`User connected: ${socket.id}`);

    socket.on('joinRoom', (roomId) => {
        handleUserJoinRoom(socket, roomId);
    });

    socket.on("sendTheOffer", (offer, roomId) => {
        socket.to(roomId).emit("receiveOffer", offer);
    });

    socket.on("sendTheAnswer", (answer, roomId) => {
        socket.to(roomId).emit("receiveAnswer", answer);
    });

    socket.on("sendIceCandidate", (candidate, roomId) => {
        socket.to(roomId).emit("receiveCandidate", candidate);
    });

    socket.on("send-message", (message, roomId) => {
        socket.to(roomId).emit("receive-message", `User ${socket.id}: ${message}`);
    });

    socket.on('disconnect', () => {
        handleUserDisconnect(socket);
    });

    function handleUserJoinRoom(socket, roomId) {
        socket.join(roomId);
        if (!roomUsers.has(roomId)) {
            roomUsers.set(roomId, new Set());
        }
        roomUsers.get(roomId).add(socket.id);
        console.log(`${socket.id} joined room: ${roomId}`);
        socket.to(roomId).emit('newJoining', `User ${socket.id} has joined the room.`);
    }

    function handleUserDisconnect(socket) {
        console.log(`User disconnected: ${socket.id}`);
        for (let [roomId, users] of roomUsers.entries()) {
            if (users.has(socket.id)) {
                users.delete(socket.id);
                socket.to(roomId).emit('userLeft', `User ${socket.id} has left the room.`, socket.id); // Kirim userId
                if (users.size === 0) {
                    roomUsers.delete(roomId);
                    console.log(`Room ${roomId} has been deleted (empty).`);
                }
            }
        }
    }
    
});


expressHTTPSServer.listen(port, '0.0.0.0', () => {
    console.log(`Server is running on port ${baseURL}`);
});
