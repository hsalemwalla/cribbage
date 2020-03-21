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
      console.log("Setting ready to true");
      window.location.href = 'game.html'

    }
  }
});
