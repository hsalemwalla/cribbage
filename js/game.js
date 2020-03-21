function Team(player1, player2) {
  jj
  this.player1 = player1;
  this.player2 = player2;
}
function Player()  {
  this.name = ""
  this.team = ""
  this.cards = ["4 clubs", "9 hearts", "8 diamods", "ace spades"]
  this.crib = []
  this.dealer = false
  this.playedCards = "7 of clubs"
}

myPlayer = new Player(); 
partner = new Player(); 
opp1 = new Player(); 
opp2 = new Player(); 

team1 = [myPlayer, partner]
team2 = [opp1, opp2]

myPlayer.name = "Hussein"
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
  data: {
    // Passed in from previous page
    playerName: "Hussein",
    myTeam: "team1",
    otherTeam: "team2",
    info: null,
    team1Points: 0,
    team2Points: 0,
    drawnCard: "7 of clubs",
    pointCount: 0
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
      console.log(this.me)
      //axios
        //.get('https://api.coindesk.com/v1/bpi/currentprice.json')
        //.then(response => (this.info = response))
      console.log("Waiting for data");
    }
  }
});
