function getParameterByName(name, url) {
  if (!url) url = window.location.href;
  name = name.replace(/[\[\]]/g, '\\$&');
  var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
    results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

var myName = getParameterByName('name'); // "lorem"


function Team(player1, player2) {
  jj
  this.player1 = player1;
  this.player2 = player2;
}
function Player()  {
  this.name = ""
  this.team = ""
  this.dealer = false
  this.playedCards = "7 of clubs"
}

myPlayer = new Player(); 
partner = new Player(); 
opp1 = new Player(); 
opp2 = new Player(); 

team1 = [myPlayer, partner]
team2 = [opp1, opp2]

myPlayer.name = myName
myPlayer.team = "team1"

partner.name = "Jillian"
partner.team = "team1"

opp1.name = "Mustafa"
opp1.team = "team2"

opp2.name = "Farhat"
opp2.team = "team2"


var BASE_URL = "http://localhost:5000/waitForPlayers";
var app = new Vue({
  el: '#game',
  data() {
    // Passed in from previous page
    return {
      playerName: myName,
      myTeam: "team1",
      otherTeam: "team2",
      info: null,
      team1Points: 0,
      team2Points: 0,
      drawnCard: "7 of clubs",
      pointCount: 0,
      componentKey: 0,
      myCards: [],
      crib: [],
      ready: false
    }
  },
  computed: {
    me() { 
      myPlayer.name = this.playerName;
      myPlayer.team = this.myTeam;
      return myPlayer
    },
    teams() { 
      return {"team1": team1, "team2": team2}
    }
  },
  methods: {
    waitForPlayers() {
      console.log("Getting my cards");
    }
  }
});

// Wait for all the players
// We will receive a "Game is ready" in the data when the 
// backend has seen all the players have joined
gameReadyEvSrc = new EventSource("http://localhost:5000/gameReady")
gameReadyEvSrc.onmessage = function(e) {
  console.log(e)
  if (e.data === "Game is ready") {
    app.ready = true;
    gameReadyEvSrc.close()
  }
}
//axios
  //.get('http://localhost:5000/gameReady')
  //.then(response => (app.ready = (response.data === 'True')))
//}

// The game is ready get my cards
//axios
  //.get('http://localhost:5000/getCardsForPlayer/'+myName)
  //.then(response => (app.myCards = response.data))
