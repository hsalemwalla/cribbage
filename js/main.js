var app = new Vue({
  el: '#main',
  data: {
    title: "Cribbage Online",
    playerName: "Hussein",
    team: "team1",
    ready: false
  },
  methods: {
    startGame: function() {
      axios .get('http://localhost:5000/addPlayer/'+this.team+'/'+this.playerName)
      var url = 'game.html?name=' + this.playerName + '&team=' + this.team
      window.location.href = url

    }
  }
});
