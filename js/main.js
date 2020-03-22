var app = new Vue({
  el: '#main',
  data: {
    title: "Cribbage Online",
    playerName: "",
    team: "team1",
    ready: false,
    serverIp: "localhost"
  },
  methods: {
    startGame: function() {
      this.$nextTick()
      var addPlayerUrl = "http://" + this.serverIp + ":5000"
      axios
        .get(addPlayerUrl + '/addPlayer/' + this.team + '/' + this.playerName)
        .then( function () {
          var url = 'game.html?name=' + this.playerName + '&team=' + this.team + '&ip=' + this.serverIp
          window.location.href = url
        })
    }
  }
});
