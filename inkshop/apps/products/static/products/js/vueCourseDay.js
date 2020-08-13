(function() {
    window.todayData = {}
    now = new Date();
    window.app = new Vue({
      el: '#app',
      data: inkshop.data.day,
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
        completed_tasks: function() {
          var completed_list = [];
          for (var i in this.one_thing_tasks) {
            var t = this.one_thing_tasks[i];
            if (t.complete) {
              completed_list.push(t);
            }
          }
          for (var i in this.today_tasks) {
            var t = this.today_tasks[i];
            if (t.complete) {
              completed_list.push(t);
            }
          }
          for (var i in this.habits) {
            var t = this.habits[i];
            if (t.complete) {
              completed_list.push(t);
            }
          }
          return completed_list
        },
        finishedLifePlanReview: function() {
          return (
            this.did_level_up_time !== null &&
            this.did_sparkle !== null &&
            this.did_hedonism !== null &&
            (this.did_write_book == true || this.did_other_book !== null) &&
            this.have_process_reflections !== null
          )
        }
      },
      methods: {
      updateDataStore: function(field_name, value) {
        console.log("updating " + field_name + " to " + value)
        var d = {}
        if (value || value === false || value === "") {
          // Got a field/value combo
          d[field_name] = value
        } else {
          var e = field_name;
          d[e.target.attributes.field_name.value] = e.target.value
        }
        console.log(d)
        for (k in d) {
          var v = d[k]
          console.log("k/v: " + k + " / " + v)
          inkshop.data.day[k] = v
          app[k] = v

        }
        console.log(inkshop.data.day)
        inkshop.sockets.daySocket.send(JSON.stringify({
            'consumerguid': inkshop.data.day.consumerguid,
            'data': inkshop.data.day
        }));
        console.log(inkshop.data.day)
      },
      updateAndSave: function(field_name, value) {
        this[field_name] = value;
        this.updateDataStore(field_name, value);
      },
      updateFromInput: function(event) {
        var field_name = e.target.attributes.field_name.value;
        var value = e.target.value;
        this.updateAndSave(field_name, value);
      },
      handleTaskEnter: function() {
        var t = {
          "title": this.next_task,
          "done": false,
        }
        this.addTask(t);
        this.next_task = "";
      },
      addTask: function(task) {
        task.order = this.today_tasks.length;
        this.today_tasks.push(task)
        this.updateDataStore('today_tasks', this.today_tasks)
      },
      removeTask: function(task) {
        var new_tasks = [];
        for (var i=0; i<this.today_tasks.length; i++){
          if (this.today_tasks[i].title != task.title) {
            new_tasks.push(this.today_tasks[i])
          }
        }
        this.today_tasks = new_tasks;
        this.updateDataStore('today_tasks', this.today_tasks)
      },
      onSortUpdate: function(event) {
        console.log("onSortUpdate")
        new_tasks = []
        old_tasks = this.today_tasks;

        old_tasks.splice(event.newIndex, 0, old_tasks.splice(event.oldIndex, 1)[0])
        var t;
        for (var j = 0; j<old_tasks.length; j++) {
          t = old_tasks[j];
          t.order = j;
          new_tasks.push(t);
        }
        this.updateDataStore('today_tasks', new_tasks)
      },
      toggleTaskComplete: function(task) {
        task.complete = !task.complete;
        this.updateDataStore('today_tasks', this.today_tasks)
        this.updateDataStore('habits', this.habits)
        this.updateDataStore('one_thing_tasks', this.one_thing_tasks)
      },
      toggleHabitComplete: function(habit) {
        habit.complete = !habit.complete;
        this.updateDataStore('habits', this.habits)
      },
      startToday: function() {
        this.startedToday = true;
        this.updateDataStore('startedToday', this.startedToday)
      },
      handleOneThingTaskEnter: function() {
        var t = {
          "title": this.next_one_thing_task,
          "done": false,
        }
        this.addOneThingTask(t);
        this.next_one_thing_task = "";
      },
      addOneThingTask: function(task) {
        task.order = this.one_thing_tasks.length;
        this.one_thing_tasks.push(task)
        this.updateDataStore('one_thing_tasks', this.one_thing_tasks)
      },
      removeOneThingTask: function(task) {
        var new_tasks = [];
        for (var i=0; i<this.one_thing_tasks.length; i++){
          if (this.one_thing_tasks[i].title != task.title) {
            new_tasks.push(this.one_thing_tasks[i])
          }
        }
        this.one_thing_tasks = new_tasks;
        this.updateDataStore('one_thing_tasks', this.one_thing_tasks)
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
  })();