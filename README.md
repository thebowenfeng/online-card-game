# online-card-game

[Livestream link](https://www.youtube.com/watch?v=X902sMF46ko)
[Server link](https://online-card-game.herokuapp.com/)


An online card game roughly based on "BigTwo", or the Chinese game "Dou Di Zhu". Supports multiple rooms thus allowing 
different games to be played simultaneously. 

## Implementation

Uses a client-server model to allow multiple players to connect to a central server and play the game. Server is built using flask-socketio and client is built using socketio. 

Utilizing socketio's "broadcasting" and "rooms" feature, multiple games could be played on the server simultaneously. 

A deployed, live server is linked above (hosted on heroku). Add this link to client.py when attempting to connect to the server. 


