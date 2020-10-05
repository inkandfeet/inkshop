window.inkshop = window.inkshop || {};
window.inkshop.auth = window.inkshop.auth || {}
window.inkshop.state = window.inkshop.state || {}
window.inkshop.methods = window.inkshop.methods || {}
window.inkshop.urls = window.inkshop.urls || {}


inkshop.auth.logout = function() {
  // console.log("Logging out..")
  localStorage.removeItem('inkshop_logged_in');
  document.location = document.location + "";
}
inkshop.auth.login = function() {
  // Set tab-shared login.
  localStorage.setItem('inkshop_logged_in', "true");
  
  // Check login via localStorage
  setInterval(function(){
  if (localStorage.getItem('inkshop_logged_in') != "true") {
      inkshop.auth.logout();
    }
  }, 1000)
  // Check login state for weird edge cases
  setInterval(function(){
    $.get(inkshop.urls.checkLogin, {}, function(resp) {
      if (resp.auth == false) {
        inkshop.auth.logout();
      }
    });
  }, 60000)
}
window.inkshop.auth.login();

inkshop.sockets = inkshop.sockets || {};
inkshop.sockets.ensureFirstConnect = function() {
  if (!app.daySocketHasConnected) {
    app.daySocketHasConnected = true;
    setTimeout(function(){
      // console.log("app.userEventHappened({'foreign': true});")
      app.userEventHappened({'foreign': true});
      // document.getElementById("inkshopDayPage" + inkshop.data.day.currentPage).scrollIntoView();
    }, 400);
  }
}
inkshop.sockets.initializeDaySocket = function() {
  inkshop.sockets.daySocket = new ReconnectingWebSocket(
      'wss://'
      + window.location.host
      + window.inkshop.urls.daySocket
  );

  inkshop.sockets.daySocket.onmessage = function(e) {
      const message = JSON.parse(e.data);
      var data = message.data;

      if (message.type == "unauthorized" && message.data.consumerguid == inkshop.constants.consumerguid) {
        inkshop.auth.logout();
      }
      if (message && message.data && message.data.consumerguid != inkshop.constants.consumerguid) {
        // console.log(message.type)

        for (k in data) {
          if (k != "consumerguid") {
            app.day[k] = data[k];
            inkshop.data.day[k] = data[k];
          }
        }
        app.userEventHappened({'foreign': true});
      }
  };
  inkshop.sockets.daySocket.onclose = function(e) {
      app.day.socketIsConnected = false;
      console.log(e);
      console.error('Chat socket closed unexpectedly');
  };
  inkshop.sockets.personSocket.onopen = function(e) {
      try {
        inkshop.data.day.socketIsConnected = true;
        app.day.socketIsConnected = true;
        inkshop.sockets.ensureFirstConnect();
      } catch {
        setTimeout(function() {
          try {
            inkshop.data.day.socketIsConnected = true;
            app.day.socketIsConnected = true;
            inkshop.sockets.ensureFirstConnect();
          } catch (e) {
            console.log("caught error on socket open")
            console.log(e)
          }
        }, 1000)
      }
      // console.log(e);
      console.log('Chat socket reopened');
  };

} 
inkshop.sockets.initializePersonSocket = function() {
  inkshop.sockets.personSocket = new ReconnectingWebSocket(
      'wss://'
      + window.location.host
      + window.inkshop.urls.personSocket
  );

  inkshop.sockets.personSocket.onmessage = function(e) {
      const message = JSON.parse(e.data);
      var data = message.data;
      // console.log("personData")
      // console.log(data)

      if (message.type == "unauthorized" && message.data && message.data.consumerguid == inkshop.constants.consumerguid) {
        inkshop.auth.logout();
      }
      if (message && message.data && message.data.consumerguid != inkshop.constants.consumerguid) {
        // console.log(message)
        // console.log(message.type)

        for (k in data) {
          if (k != "consumerguid") {
            app.person[k] = data[k];
            inkshop.data.person[k] = data[k];
          }
        }
        app.userEventHappened({'foreign': true});
      }
  };
  inkshop.sockets.personSocket.onclose = function(e) {
      app.day.socketIsConnected = false;
      console.log(e);
      console.error('Chat socket closed unexpectedly');
  };
  inkshop.sockets.personSocket.onopen = function(e) {
      try {
        inkshop.data.day.socketIsConnected = true;
        app.day.socketIsConnected = true;
        inkshop.sockets.ensureFirstConnect();
      } catch {
        setTimeout(function() {
          try {
            inkshop.data.day.socketIsConnected = true;
            app.day.socketIsConnected = true;
            inkshop.sockets.ensureFirstConnect();
          } catch (e) {
            console.log("caught error on socket open")
            console.log(e)
          }
        }, 1000)
      }
      // console.log(e);
      console.log('Chat socket reopened');
  };

}

inkshop.methods.generateUID = function(len) {
   var result           = '';
   var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
   var charactersLength = characters.length;
   for ( var i = 0; i < len; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
}
inkshop.methods.startConfetti = function() {
  if (!inkshop.state.confettiStarted) {
    confetti.start(30000);
    inkshop.state.confettiStarted = true;
  }
}
inkshop.methods.stopConfetti = function() {
  confetti.stop();
}
