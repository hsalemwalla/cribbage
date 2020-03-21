function getParameterByName(name, url) {
  if (!url) url = window.location.href;
  name = name.replace(/[\[\]]/g, '\\$&');
  var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
    results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

var myName = getParameterByName('name')
var myTeam = getParameterByName('team')

function Player()  {
  this.name = ""
  this.team = ""
  this.dealer = false
  this.playedCards = "7 of clubs"
}


//var BASE_URL = "http://localhost:5000/waitForPlayers";

var app = new Vue({
  el: '#game',
  data() {
    // Passed in from previous page
    return {
      playerName: myName,
      team: myTeam,
      players: [],
      team1Points: 0,
      team2Points: 0,
      drawnCard: null,
      pointCount: 0,
      myCards: [],
      crib: [],
    }
  },
  methods: {
    playCard(e) {
      console.log(e.target.innerText);
      axios.get('http://localhost:5000/playCard/'+myName+'/'+e.target.innerText)
    }
  }
});

// Wait for all the players
// We will receive a "Game is ready" in the data when the 
// backend has seen all the players have joined
gameReadyEvSrc = new EventSource("http://localhost:5000/gameReady")
gameReadyEvSrc.onmessage = function(e) {
  console.log(e)
  var data = JSON.parse(e.data)
  if (data.ready === "True") {
    // Find the index on players that I am at
    myIdx = 0;
    data.player_names.forEach( function(item, idx) {
      if (item.name === myName) {
        myIdx = idx
      }
    })
    // Update the player names
    var tmp = data.player_names
    var playerNames = tmp.splice(myIdx)
    
    playerNames = playerNames.concat(tmp)
    playerNames.forEach(function(item, idx) {
      player = new Player()
      player.name = item.name
      player.team = item.team
      app.players.push(player)
    })
    gameReadyEvSrc.close()

    axios
      .get('http://localhost:5000/getCardsForPlayer/'+myName)
      .then(response => (app.myCards = response.data))
  }
}

// The game is ready get my cards
