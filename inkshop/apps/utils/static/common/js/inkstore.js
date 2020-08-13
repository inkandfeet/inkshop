window.inkshop = window.inkshop || {};
window.inkshop.auth = window.inkshop.auth || {}
window.inkshop.urls = window.inkshop.urls || {}


inkshop.auth.logout = function() {
  localStorage.removeItem('inkshop_logged_in');
  document.location = document.location + "";
}
inkshop.auth.login = function() {
  // Set tab-shared login.
  localStorage.setItem('inkshop_logged_in', "true");
  
  // Check login via localStorage
  setInterval(function(){
  if (localStorage.getItem('inkshop_logged_in') != "true") {
      logout();
    }
  }, 1000)
  // Check login state for weird edge cases
  setInterval(function(){
    $.get(inkshop.urls.checkLogin, {}, function(resp) {
      if (resp.auth == false) {
        logout();
      }
    });
  }, 60000)
}
window.inkshop.auth.login();

inkshop.sockets = inkshop.sockets || {};
inkshop.sockets.initializeDaySocket = function() {
  inkshop.sockets.daySocket = new ReconnectingWebSocket(
      'wss://'
      + window.location.host
      + window.inkshop.urls.daySocket
  );

  inkshop.sockets.daySocket.onmessage = function(e) {
      const message = JSON.parse(e.data);
      var data = message.data;

      console.log(message)
      console.log(message.type)
      if (message.type == "unauthorized" && message.data.consumerguid == inkshop.data.day.consumerguid) {
        // document.location.reload();
        logout();
      }

      for (k in data) {
        if (k != "consumerguid") {
          app[k] = data[k];
          inkshop.data.day[k] = data[k];
        }
    }
  };
  inkshop.sockets.daySocket.onclose = function(e) {
      console.log(e);
      console.error('Chat socket closed unexpectedly');
  };
}
