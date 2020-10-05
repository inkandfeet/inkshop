$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });
});

(function() {
    window.todayData = {}
    now = new Date();
    Vue.config.devtools = true;
    window.app = new Vue({
      el: '#inkshopApp',
      data: {
        day: inkshop.data.day,
        person: inkshop.data.person,
        startedToday: false,
        timeRemainingString: "",
        secondsStr: "",
        timeRemaining: moment.duration(0),
        minutesRemaining: 0,
        daySocketHasConnected: false,
        constants: inkshop.constants,
      },
      computed: {
        phase: function() {
          if (!this.startedToday) {
            return "plan";
          }
          if (this.startedLifePlanReview) {
            if (this.finishedDailyReview) {
              return "relax;"
            } else {
              return "review";
            }
          }
          return "do";
        },
        getJourney: function() {
          try {
            // console.log("getJourney")
            // console.log(inkshop.data.person)
            // console.log(inkshop.data.person.products.sprint[inkshop.constants.journeyguid])
            return inkshop.data.person.products.sprint[inkshop.constants.journeyguid]

          } catch (e) {
            console.log(e)
          }
        }
      },
      methods: {
        updateDataStore: function(field_name, value) {
          store = field_name.split(".")[0];
          field_name = field_name.slice(store.length +1);

          console.log("updating " + store + "." + field_name + " to " + value)
          console.log("store: " + store)

          var d = {}
          var working_key = "";

          if (value || value === false || value === "" || value === null) {
            // Got a field/value combo
            working_key = field_name;
          } else {
            var e = field_name;
            working_key = e.target.attributes.field_name.value;
            value = e.target.value;
          }
          console.log("working_key: " + working_key)
          // console.log("value")
          // console.log(value)

          if (store =="journey") {
            store = "person";
            working_key = 'products.sprint.' + inkshop.constants.journeyguid + "." + field_name
            // console.log("adjusting field_name to journey namespace: " + field_name )
          }
          switch (true) {
            case (store == "day"):
              inkshop_data_target = inkshop.data.day
              break;
            case (store == "person"):
              inkshop_data_target = inkshop.data.person
              break;
          }
          app_data_target = app
          this_data_target = this

          if (working_key.indexOf(".") == -1) {
            // d[working_key] = value;
            inkshop_data_target[working_key] = value;
            app_data_target[working_key] = value;
            this_data_target[working_key] = value;
          } else {
            data_target = d;
            components = working_key.split(".")
            // console.log(components)
            num_components = components.length -1;
            // console.log(num_components)
            for (i in components) {
              // console.log(i);
              if (i<num_components) {
                // console.log("inside loop inkshop_data_target")
                // console.log(inkshop_data_target)
                // console.log(components[i])
                // console.log(inkshop.data.day)
                inkshop_data_target[components[i]] = inkshop_data_target[components[i]] || {};
                inkshop_data_target = inkshop_data_target[components[i]];
                app_data_target[components[i]] = app_data_target[components[i]] || {};
                app_data_target = app_data_target[components[i]];
                this_data_target[components[i]] = this_data_target[components[i]] || {};
                this_data_target = this_data_target[components[i]];

              } else {
                // console.log("updating inkshop_data_target")
                // console.log(inkshop_data_target)
                // console.log(components[i])
                // console.log(inkshop.data.day)
                // console.log(value)
                inkshop_data_target[components[i]] = value
                app_data_target[components[i]] = value
                this_data_target[components[i]] = value

              }
            }
          }
          

          // console.log(inkshop.data.day)
          // Batch updates to 1/sec max.
          // clearTimeout(inkshop.sockets.daySocketQueue);
          // inkshop.sockets.daySocketQueue = setTimeout(function() {
            // console.log("sending")
            // console.log("store:" + store)
            // console.log({
            //       'consumerguid': inkshop.constants.consumerguid,
            //       'data': inkshop.data.person
            //     })
            // console.log(inkshop.data.person)
            try {
              switch (true) {
                case (store == "day"):
                  // inkshop_data_target = inkshop.data.day
                  inkshop.sockets.daySocket.send(JSON.stringify({
                    'consumerguid': inkshop.constants.consumerguid,
                    'data': inkshop.data.day
                  }));
                  break;
                case (store == "person"):
                  // inkshop_data_target = inkshop.data.person
                  inkshop.sockets.personSocket.send(JSON.stringify({
                    'consumerguid': inkshop.constants.consumerguid,
                    'data': inkshop.data.person
                  }));
                  break;
              }

            } catch(e) {
              console.log(e)
            }
            // if (store == "day") {
            // } 
            // else if (store == "person") {
            //   inkshop.sockets.personSocket.send(JSON.stringify({
            //     'consumerguid': inkshop.constants.consumerguid,
            //     'data': inkshop.data.person
            //   }));
            // }
          // }, 500);
          app.userEventHappened();
          // setTimeout(function(){
          //   console.log("app.userEventHappened();")
          //   app.userEventHappened();

          // }, 50)
          
          // console.log(inkshop.data.day)
        },
        updateAndSaveFromAttrs: function(e) {
          // console.log("updateAndSaveFromAttrs")
          // console.log(e)
          var field_name = e.target.attributes.field_name.value;
          var value = e.target.attributes.value.value;
          if (value === "true") {
            value = true;
          }
          if (value === "false") {
            value = false;
          }
          this.updateAndSave(field_name, value)
        },
        updateAndSave: function(field_name, value) {
          // this[field_name] = value;
          this.updateDataStore(field_name, value);
        },
        updateFromInput: function(event) {
          var field_name = e.target.attributes.field_name.value;
          var value = e.target.value;
          this.updateAndSave(field_name, value);
        },
        scrollToCurrentPage: function(data) {
          console.log("scrollToCurrentPage")
          console.log(data)
          console.log(inkshop.data.day.currentPage)
          var old_page = data.old_page;

          if (inkshop.data.day.currentPage != old_page || (data && data['foreign'] == true)) {
            // console.log("Scrolling because " + inkshop.data.day.currentPage + " vs " + old_page + " or data[foreign]:" + data["foreign"] )
            try {
              document.getElementById("inkshopDayPage" + inkshop.data.day.currentPage).scrollIntoView();
            } catch(e) {
              
            }
            setTimeout(function(){
              // console.log("Scrolling delay to inkshopDayPage" + inkshop.data.day.currentPage)
              document.getElementById("inkshopDayPage" + inkshop.data.day.currentPage).scrollIntoView();
              /* var newStateScrollPosition = window.pageYOffset + document.getElementById("inkshopDayPage" + inkshop.data.day.currentPage).getBoundingClientRect().top - 130;
              if (newStateScrollPosition < 0) {
                newStateScrollPosition = 0;
              }
              

              console.log(document.getElementById("inkshopDayPage" + inkshop.data.day.currentPage))
              console.log(document.getElementById("inkshopDayPage" + inkshop.data.day.currentPage).getBoundingClientRect().top)
              console.log("scrollTop should be " + newStateScrollPosition)
              console.log("scrollTop is" + document.body.scrollTop)
              console.log("inkshop.state.lastUserScrollAt" + inkshop.state.lastUserScrollAt)
              console.log("inkshop.state.stateBasedLastScroll" + inkshop.state.stateBasedLastScroll)

              // I'm not clear on this logic. When would we not?
              // if (
              //   {# We're not at the correct scroll position #}
              //   document.body.scrollTop != inkshop.state.stateBasedCurrentScrollPosition
              //   {# The user hasn't scrolled more recently than the last time the state-based scroll changed #}
              //   && (inkshop.state.lastUserScrollAt < inkshop.state.stateBasedLastScroll || inkshop.state.lastUserScrollAt == 0)
              // ) {
                console.log("scrolling")
                inkshop.state.stateBasedLastScroll = new Date();
                window.scrollTo(0, newStateScrollPosition);
              // }
              inkshop.state.stateBasedCurrentScrollPosition = newStateScrollPosition; */
            }, 350)

          } else {
            if (data) {
              console.log("Not scrolling because " + inkshop.data.day.currentPage + " vs " + old_page + " or data[foreign]:" + data["foreign"] )
            }
          }
        },
        userEventHappened: function(data) {
          console.log('event')
          console.log(data)
          // Triggers state recalculation.
          try {
            this.day.userEventHappened(data)
          } catch (e) {
            console.log(e)
          }
        },
        resetDay: function() {
          if (window.confirm("Are you sure you want to reset all of today\'s data?\n\nThere is no way to undo this.\n\nPress OK to DELETE today's data.\nPress Cancel to KEEP today's data.")) {
            inkshop.methods.stopConfetti();
            try {
              inkshop.data.day.resetDay();
            } catch (e) {
              console.log("Error resettting day")
              consoe.log(e)
            }
            inkshop.data.day = {}
            this.startedToday =  false;
            this.timeRemainingString =  "";
            this.secondsStr =  "";
            this.timeRemaining =  moment.duration(0);
            for (k in inkshop.data.dayDefaults) {
                if (k != "socketHasConnected" && k !=  "socketIsConnected") {
                  inkshop.data.day[k] = inkshop.data.dayDefaults[k];
                  this.day[k] = inkshop.data.dayDefaults[k];
                  if (typeof(inkshop.data.dayDefaults[k]) != typeof(function(){})) {
                    try {
                      this.updateDataStore("day." + k, inkshop.data.dayDefaults[k])
                    } catch (e) {
                      console.error(e);
                    }
                  }
                }
            }
            this.userEventHappened();
            setTimeout(function(){
              document.location = document.location + "";
            }, 750)
          }
        },
        startToday: function() {
          this.day.startedToday = true;
          this.day.startedTodayAt = moment(new Date());
          this.day.shouldEndTodayAt = moment(this.startedTodayAt).add(1, 'hours');
          this.day.timerRunning = true;
          this.updateDataStore('day.startedToday', this.day.startedToday);
          this.updateDataStore('day.startedTodayAt', this.day.startedTodayAt);
          this.updateDataStore('day.shouldEndTodayAt', this.day.shouldEndTodayAt);
          this.updateDataStore('day.timerRunning', this.day.timerRunning);
          this.userEventHappened();
        },
        finishToday: function() {
          this.day.finishedToday = true;
          this.day.finishedTodayAt = moment(new Date());
          this.day.complete = true;
          this.day.timerRunning = false;
          this.updateDataStore('day.finishedToday', this.day.finishedToday);
          this.updateDataStore('day.finishedTodayAt', this.day.finishedTodayAt);
          this.updateDataStore('day.complete', this.day.complete);
          this.updateDataStore('day.timerRunning', this.day.timerRunning);
          this.userEventHappened();
        },
        pauseToday: function() {
          this.day.timerRunning = false;
          this.updateDataStore('day.timerRunning', this.day.timerRunning);
        },
        resumeToday: function() {
          this.day.shouldEndTodayAt = moment(new Date()) + this.timeRemaining;
          this.updateDataStore('day.shouldEndTodayAt', this.day.shouldEndTodayAt);
          this.day.timerRunning = true;
          this.updateDataStore('day.timerRunning', this.day.timerRunning);
        },
        tickTimeRemaining: function() {
          if (this.day.timerRunning) {
            var now = moment(new Date());
            var remaining =  moment.duration(moment(this.day.shouldEndTodayAt).diff(now));
            // console.log("remaining: " + remaining.asSeconds())
            // console.log(now)
            // console.log(new Date())
            // console.log(this.day.shouldEndTodayAt)
            // console.log(remaining.asMinutes())
            if (remaining.asSeconds() > 0) {
              this.timeRemaining = remaining;
              this.minutesRemaining = Math.floor(remaining.asMinutes());
              var secondsStr = (remaining.seconds() < 10) ? "0" + remaining.seconds(): remaining.seconds();
              this.timeRemainingString = Math.floor(remaining.asMinutes()) + ":" + secondsStr;
              this.secondsStr = secondsStr;
            } else {
              this.minutesRemaining = 0;
              this.timeRemaining = moment.duration(0)
              this.timeRemainingString = "00:00"
              this.secondsStr = "00"
            }
            try {
              this.day.timerTicked();
            } catch (e) {}
            // this.updateDataStore('day.timeRemainingString', this.day.timeRemainingString);
            // return this.shouldEndTodayAt - moment(new Date());
          }
          setTimeout(app.tickTimeRemaining, 1000)
        },
        handleOneThingTaskEnter: function() {
          var t = {
            "title": this.next_one_thing_task,
            "done": false,
          }
          this.addOneThingTask(t);
          this.next_one_thing_task = "";
        },
        addOtherTasks: function() {
          this.updateAndSave('oneThingDone', true)
        },
        markTaskHappy: function(task) {
          task.makesMeHappy = !task.makesMeHappy;
          this.updateDataStore('today_tasks', this.today_tasks)
          this.updateDataStore('one_thing_tasks', this.one_thing_tasks)
          this.updateDataStore('habits', this.habits)
        },
        startLifePlanReview: function() {
          this.updateAndSave('startedLifePlanReview', true)
          this.updateAndSave('phase_override', null)
        },
        showMoreHoursMaking: function() {
          this.updateAndSave('moreHoursMakingShown', true)
        },
        setHoursMaking: function(hours) {
          this.updateAndSave('hoursMaking', hours)
        },
        setHoursClarity: function(hours) {
          this.updateAndSave('hoursClarity', hours)
        },
        toggleCountry: function(country_code) {
          this.updateAndSave("adventured_in_" + country_code, !this["adventured_in_" + country_code])
        },
      }
    })
    app.tickTimeRemaining();
  })();