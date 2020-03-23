function getParameterByName(name, url) {
  if (!url) url = window.location.href;
  name = name.replace(/[\[\]]/g, '\\$&');
  var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
    results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

function getScoreTrack(score) {
  if (score < 0) {
    return ""
  }
  var track = ""
  for (var i = 0; i < score; i++) {
    if (i % 5 === 0) {
      track += "|"
    }
    track += "."
  }

  return track
}

var myName = getParameterByName('name')
var myTeam = getParameterByName('team')
var ip = getParameterByName('ip')

function Player()  {
  this.name = ""
  this.team = ""
  this.playedCards = ""
  this.dealer = ""
}


function getCardValue(card) {
  var value = card.split(' ')[0]
  if (value === 'A') { return 1 }
  else if (value === 'J') { return 10 }
  else if (value === 'Q') { return 10 }
  else if (value === 'K') { return 10 }
  else { return parseInt(value) }
}

var app = new Vue({
  el: '#game',
  data() {
    // Passed in from previous page
    return {
      playerName: myName,
      team: myTeam,
      players: [],
      team1Points: 0,
      team1ScoreTrack: "",
      team2Points: 0,
      team2ScoreTrack: "",
      drawnCard: null,
      pointCount: 0,
      myCards: [],
      crib: "",
      myTurn: false,
      phase: 'init',
      nextRoundAvail: false,
      allDone: false,
      isPlayerTurn: [false,false,false,false]
    }
  },
  methods: {
    updateScore(e) {
      switch(e.currentTarget.id) {
        case 'team1ScoreIncrease':
          this.team1Points = parseInt(this.team1Points) + 1
          axios.get('http://'+ ip + '/score/team1/'+this.team1Points)
          break;
        case 'team1ScoreDecrease':
          this.team1Points = parseInt(this.team1Points) - 1
          axios.get('http://'+ ip + '/score/team1/'+this.team1Points)
          break;
        case 'team2ScoreIncrease':
          this.team2Points = parseInt(this.team2Points) + 1
          axios.get('http://'+ ip + '/score/team2/'+this.team2Points)
          break;
        case 'team2ScoreDecrease':
          this.team2Points = parseInt(this.team2Points) - 1
          axios.get('http://'+ ip + '/score/team2/'+this.team2Points)
          break;
      }
    },
    selectCard(e) {
      if (this.phase === 'select_crib') {
        console.assert(this.myCards.length === 5, "myCards is not 5") 
        // Go through my cards, find the card, and kill it
        var cribCard = null
        for (var i = 0; i < this.myCards.length; i++) {
          if (this.myCards[i] === e.target.innerText) {
            // Get rid of one card
            cribCard = this.myCards.splice(i,1)
          }
        }
        console.assert(cribCard != null, "cribCard is null")
        axios.get('http://'+ ip + '/addToCrib/'+myName+'/'+e.target.innerText)
        .then(getMyCards)
      } else if (this.phase === 'pointing') {
        if (this.nextRoundAvail) {
          // Only the next round avail button is valid
          if (e.target.innerText === "Next Round") {
            axios.get('http://'+ ip + '/nextRound')
          }
        } else {
          if (e.target.innerText === "Pass") {
            axios.get('http://'+ ip + '/playCard/'+myName+'/'+e.target.innerText)
          } else {
            // Go through my cards, find the card, and kill it
            var cardToPlay = null
            // Check the card we selected is valid
            // Check it's my turn
            // Check it doesn't exceed count
            if (!this.myTurn) {
              return
            }
            if (getCardValue(e.target.innerText) + this.pointCount > 31) {
              return
            }
            for (var i = 0; i < this.myCards.length; i++) {
              if (this.myCards[i] === e.target.innerText) {
                // Get rid of one card
                cardToPlay = this.myCards.splice(i,1)
              }
            }
            console.assert(cardToPlay != null, "playing card is null")
            console.log(e.target.innerText);
            axios.get('http://'+ ip + '/playCard/'+myName+'/'+e.target.innerText)
          }
        }
      } else if (this.phase === 'counting') {
        if (e.target.innerText === "Pass") {
          axios.get('http://'+ ip + '/playCard/'+myName+'/cribNextTurn')
        }
      }
    },
    newHand(e) {
      console.log(e)
      this.allDone = false
      axios.get('http://'+ ip + '/newHand')
    }
  }
});


/**
 * Pointing phase
 */
function pointing() {
  // begin event source for pointing
  // Also start accepting card played events
  pointingEvSrc = new EventSource("http://" + ip + "/pointing")
  pointingEvSrc.onerror = function(e) {
    console.log(e)
  }
  pointingEvSrc.onmessage = function(e) {
    console.log(e)
    var data = JSON.parse(e.data)

    if (data.phase === 'pointing') {

      // The new count after the person played
      app.pointCount = data.new_count
      app.drawnCard = data.card_flipped
      app.nextRoundAvail = data.next_round_avail

      // Is it my turn? 
      app.myTurn = (data.player_turn === myName)

      // Set the current players turn
      // Set dealer while we're at it
      var player_num_turn = -1;
      for (var i = 0; i < app.players.length; i++) {
        app.isPlayerTurn[i] = (app.players[i].name === data.player_turn)
        if (app.players[i].name === data.dealer) {
          app.players[i].dealer = "Dealer"
        } else {
          app.players[i].dealer = ""
        }
      }

      // Go through each player, filter out the array with cards that this player played
      // Then set the players playedCards to the last in the list
      app.players.forEach( function(player, idx) {
        var cardsPlayedByPlayer = data.round_play.filter(function(play) {
          return player.name == play.player
        })
        player.playedCards = ""
        if (cardsPlayedByPlayer.length != 0) {
          player.playedCards = cardsPlayedByPlayer[cardsPlayedByPlayer.length-1].card
        }
      })

      // scores
      app.team1Points = data.scores.team1
      app.team2Points = data.scores.team2
      app.team1ScoreTrack = getScoreTrack(app.team1Points)
      app.team2ScoreTrack = getScoreTrack(app.team2Points)
    } else {
      if (data.phase === 'counting') {
        app.pointCount = data.new_count
        app.drawnCard = data.card_flipped
        app.nextRoundAvail = data.next_round_avail

        // Update whos turn it is
        var player_num_turn = -1;
        for (var i = 0; i < app.players.length; i++) {
          app.isPlayerTurn[i] = (app.players[i].name === data.player_turn)
          if (app.players[i].name === data.dealer) {
            app.players[i].dealer = "Dealer"
          } else {
            app.players[i].dealer = ""
          }
        }
        // Set played cards to "" for each player
        app.players.forEach( function(player, idx) {
          player.playedCards = ""
        })

        // Scores
        app.team1Points = data.scores.team1
        app.team2Points = data.scores.team2
        app.team1ScoreTrack = getScoreTrack(app.team1Points)
        app.team2ScoreTrack = getScoreTrack(app.team2Points)
        pointingEvSrc.close()
        getMyCards()

      }
    }
  }
}

function counting() {
  countingEvSrc = new EventSource("http://" + ip + "/counting")
  countingEvSrc.onerror = function(e) {
    console.log(e)
  }
  countingEvSrc.onmessage = function(e) {
    console.log(e)
    var data = JSON.parse(e.data)

    // The new count after the person played
    app.drawnCard = data.card_flipped
    // Show the next round avail button, and hide the pass button


    // Is it my turn? 
    app.myTurn = (data.player_turn === myName)

    // Dealer and player turn
    var player_num_turn = -1;
    for (var i = 0; i < app.players.length; i++) {
      // Set the players cards
      app.players[i].playedCards = ""
      data.all_cards[app.players[i].name].forEach(function(card, idx) {
        app.players[i].playedCards += card
        app.players[i].playedCards += "\n"
      })

      // Whos turn is it
      app.isPlayerTurn[i] = (app.players[i].name === data.player_turn)

      // Set dealer
      if (app.players[i].name === data.dealer) {
        app.players[i].dealer = "Dealer"
      } else {
        app.players[i].dealer = ""
      }
    }

    // Set the crib

    app.crib = ""
    data.all_cards['crib'].forEach(function(card, idx) {
      app.crib += card
      app.crib += "\n"
    })

    // Scores
    app.team1Points = data.scores.team1
    app.team2Points = data.scores.team2
    app.team1ScoreTrack = getScoreTrack(app.team1Points)
    app.team2ScoreTrack = getScoreTrack(app.team2Points)

    // Show the newHand button and close this event source
    app.allDone = data.all_done_counting
    if (data.reset) {
      countingEvSrc.close()
      getMyCards()
    }
  }
  console.log("Starting counting phase")
}


function getMyCards() {
  // Clean my shit up
  if (app.phase === 'init') {
    app.phase = 'select_crib'
  } else if (app.phase === 'select_crib') {
    app.phase = 'pointing'
  } else if (app.phase === 'pointing') {
    app.phase = 'counting'
  } else if (app.phase === 'counting') {
    app.phase = 'select_crib'
  }

  // Clean up unless we are moving from pointing->counting
  if (app.phase != 'counting') {
    app.drawnCard = null
    app.pointCount = 0
    app.myCards = []
    app.crib = ""
    app.myTurn = false
    app.nextRoundAvail = false
    app.allDone = false
    app.isPlayerTurn = [false,false,false,false]
    app.players.forEach(function(player, idx) {
      player.playedCards = ""
    })
  }
  
  axios
    .get('http://' + ip + '/getDealerName/'+myName)
    .then(function(response) {
      // Go through and set the dealer
      app.players.forEach(function(player, idx) {
        if (player.name == response.data) {
          player.dealer = "Dealer"
        }
      })
    })

  
  axios
    .get('http://' + ip + '/getCardsForPlayer/'+myName)
    .then(function(response) {
      app.myCards = response.data
      if (app.phase === 'pointing') {
        pointing()
      } else if (app.phase === 'counting') {
        counting()
      }
    })
}

// Wait for all the players
// We will receive a "Game is ready" in the data when the 
// backend has seen all the players have joined
gameReadyEvSrc = new EventSource("http://" + ip + "/gameReady")
gameReadyEvSrc.onerror = function(e) {
  console.log(e)
}
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

    getMyCards()

    //pointing()
  }
}

// The game is ready get my cards
