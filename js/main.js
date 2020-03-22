var app = new Vue({
  el: '#main',
  data: {
    title: "Cribbage Online",
    playerName: "",
    team: "team1",
    ready: false,
    serverIp: "localhost:5000"
  },
  methods: {
    startGame: function() {
      this.$nextTick()
      var addPlayerUrl = "http://" + this.serverIp
      var self = this
      axios
        .get(addPlayerUrl + '/addPlayer/' + this.team + '/' + this.playerName)
        .then( function () {
          var url = 'game.html?name=' + self.playerName + '&team=' + self.team + '&ip=' + self.serverIp
          window.location.href = url
        })
    }
  }
});
