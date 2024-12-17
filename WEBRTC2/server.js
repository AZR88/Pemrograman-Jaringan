const express = require('express');
const http = require('http');
const { v4: uuid } = require('uuid');
const socketIO = require('socket.io');
const app = express();
const expressHTTPServer = http.createServer(app);
const io = new socketIO.Server(expressHTTPServer);

// Mendeklarasikan roomUsers sebagai Map untuk menyimpan data pengguna per ruangan
let roomUsers = new Map();

app.use(express.static('public'));
app.set('view engine', 'ejs');

const port = 3001;
const baseURL = `http://localhost:${port}/`; // Base URL including port

app.get('/', (req, res) => {
    const roomId = uuid();  // Generate new room ID
    const roomLink = `${baseURL}${roomId}`; // Create the full room link
    console.log(`Server running at: ${baseURL}`);  // Log the server URL
    console.log(`Generated new room link: ${roomLink}`);  // Log the room link
    res.redirect(`/${roomId}`);
});

app.get("/:roomId", (req, res) => {
    const roomId = req.params.roomId;
    const roomLink = `${baseURL}${roomId}`; // Create the full room link
    console.log(`Accessed room: ${roomLink}`);  // Log the room access link
    res.render('index', {
        roomId
    });
});

io.on('connection', (socket) => {
    console.log(`User connected: ${socket.id}`);

    // Handle user joining a room
    socket.on('joinRoom', (roomId) => {
        handleUserJoinRoom(socket, roomId);
    });

    // Send the offer
    socket.on("sendTheOffer", (offer, roomId) => {
        socket.to(roomId).emit("receiveOffer", offer);
    });

    // Send the answer
    socket.on("sendTheAnswer", (answer, roomId) => {
        socket.to(roomId).emit("receiveAnswer", answer);
    });

    // Send Ice candidate
    socket.on("sendIceCandidate", (candidate, roomId) => {
        socket.to(roomId).emit("receiveCandidate", candidate);
    });

    // Listen for "send-message" from clients and broadcast to the room
    socket.on("send-message", (message, roomId) => {
        socket.to(roomId).emit("receive-message", message);  // Broadcast message to the room
    });

    // Handle user leaving a room
    socket.on('disconnect', () => {
        handleUserDisconnect(socket);
    });

    // Function to handle user joining a room
    function handleUserJoinRoom(socket, roomId) {
        socket.join(roomId);

        // Initialize room in roomUsers map if it doesn't exist
        if (!roomUsers.has(roomId)) {
            roomUsers.set(roomId, new Set());
        }
        roomUsers.get(roomId).add(socket.id); // Add user to the room

        console.log(`${socket.id} joined room: ${roomId}`);
        socket.to(roomId).emit('newJoining', `A user has joined the room.`);
    }

    // Handle user disconnecting
    function handleUserDisconnect(socket) {
        console.log(`User disconnected: ${socket.id}`);

        // Check all rooms to find where the user was
        for (let [roomId, users] of roomUsers.entries()) {
            if (users.has(socket.id)) {
                users.delete(socket.id); // Remove user from the room
                socket.to(roomId).emit('userLeft', `A user has left the room.`);

                // Clean up the room if it's empty
                if (users.size === 0) {
                    roomUsers.delete(roomId);  // Delete the room from map if empty
                    console.log(`Room ${roomId} has been deleted (empty).`);
                }
            }
        }
    }
});

expressHTTPServer.listen(port, () => {
    console.log(`Server is running on port ${baseURL}`);
});