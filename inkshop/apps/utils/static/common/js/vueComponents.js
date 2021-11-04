Vue.component('editable',{
  template:'<span :id=\'ele_id\' :data-cy="ele_id" v-bind:class="{ \'editable_field\': true, \'big\': big  && big != \'medium\', \'medium\': big == \'medium\', \'bold\': bold, \'underline\': underline, \'empty\': shadowContent == \'\' || !focused, }" contenteditable="true" @focus="focused" @blur="blurred" v-on:keyup.enter="enterPressed" v-on:keydown.tab="tabPressed" v-on:keyup="keyUp" :key="renderKey">{{ shadowContent }}</span>',
  props:['content', 'big', 'bold', 'underline', 'enter_focus', 'multiline', 'keyuphandler', 'wait_for_ms'],
  mounted:function(){
    // console.log("mounted")
    // console.log(this.content)
    this.$el.innerText = (this.content) ? (this.content + " ").trim() : "";
    this.lastUpdatedValue = this.$el.innerText;
    this.ele_id = this.$el.attributes.field_name.value.replace(".name", "").replaceAll(".", "_") || false;
    this.multiline = this.multiline == "true";
    this.wait_for = (this.wait_for_ms) ? 1.0 * this.wait_for_ms : 1000
    this.shadowContent = (this.content != undefined)? (this.content + " ").trim() : "";

  },
  data: function() {
    return {
      'ele_id': 'blank',
      'is_empty': '',
      'shadowContent': '',
      'focused': false,
      'renderKey': 0,
    }
  },
  updated: function() {
    this.shadowContent = (this.content != undefined)? (this.content + " ").trim() : "";
  },
  watch: {
    content: function(val) {
      if (!this.focused && this.$el.innerText != val) {
        this.shadowContent = (val != undefined) ? (val + " ").trim() : "";
        this.content = (val != undefined) ? (val + " ").trim() : "";
        this.renderKey ++;
      }
    }
  },
  computed: {
    currentText: function(){
      try {
        if (this.focused) {
          return this.shadowContent;
        } else {
          return this.content;
        }
      } catch {}
    }
  },
  methods:{
    update: function(event){
      // saveSelection();
      inkshop.state.queuedContext = null;
      // clearTimeout(this.queuedUpdate);
      // console.log(event.target.attributes)
      // console.log(event.target)
      if( event.target.attributes.object != undefined) {
        this.$emit('update', event.target.attributes.object.value, event.target.attributes.object_key.value, event.target.innerText.trim());
        // console.log("emitted")
      } else {
        this.$emit('update', event.target.attributes.field_name.value, event.target.innerText.trim());
        // console.log("emitted")
      }
      this.lastUpdatedValue = event.target.innerText;
    },
    focused: function(event) {
      // console.log("focused")
      this.focused = true;
    },
    blurred: function(event) {
      // console.log("blurred")
      this.focused = false;
      this.update(event);
    },
    enterPressed: function(event) {
      try {
        event.target.blur();
        document.getElementById(this.enter_focus).focus()
      } catch {
        event.target.blur();
      }
      if (!this.multiline) {
        event.target.innerText = event.target.innerText.trim()
      }
      event.preventDefault();
      return false;
    },
    tabPressed: function(event) {

      // this.update(event);
      if (this.enter_focus) {
        event.preventDefault();
        try {
          event.target.blur();
          setTimeout(function(ele_id) {
            try {
              document.getElementById(ele_id).focus()
            } catch {
              
            }
          }, 10, this.enter_focus);
        } catch (e) {
          // console.error(e)
          event.target.blur();
        }
        return false;
      }
    },
    keyUp: function(event) {
      try {
        // console.log(event.target.innerText);
        // var selectionStart = event.target.selectionStart;
        // console.log(selectionStart)
        clearTimeout(this.updateTimeout);
        if (event.target.innerText != "") {
          this.updateTimeout = setTimeout(function() {
            this.update(event)
          }.bind(this), this.wait_for);
        } else {
          this.update(event);
        }
        // event.target.selectionStart = selectionStart;
        // setTimeout(function(){
        //   event.target.selectionStart = selectionStart;
        // })
        // this.currentValue = event.target.innerText;
        // clearTimeout(this.queuedUpdate);
        // inkshop.state.queuedContext = null;
        // if (this.currentValue != this.lastUpdatedValue) {
        //   inkshop.state.queuedContext = this;
        //   this.queuedUpdate = setTimeout(function(){
        //     if( event.target.attributes.object != undefined) {
        //       inkshop.state.queuedContext.$emit('update', event.target.attributes.object.value, event.target.attributes.object_key.value, event.target.innerText);
        //     } else {
        //       inkshop.state.queuedContext.$emit('update', event.target.attributes.field_name.value, event.target.innerText);
        //     }

        //   }, 200);
        // };
        //     app.userEventHappened();
        // console.log(event)
        // this.shadowContent
        // if (event.key == "Delete") {
        //   this.shadowContent = this.shadowContent.slice(0, -1);
        // } else {
        //   if (event.key == "Backspace") {
        //     this.shadowContent = this.shadowContent.slice(0, -1);
        //   } else {
        //     if (event.key.length == 1) {
        //       this.shadowContent += event.key;
        //     }
        //   }
        // }


        if (this.keyuphandler) {
          this.keyuphandler(event, event.target.attributes.field_name.value, event.target.innerText)
        }
        // this.$emit('focused_on', this.ele_id)
      } catch (e) {
        console.error(e)
      }
    },
  }
});

Vue.component('page',{
  template:'<div v-bind:class="{\'inkshopPage\':true, \'active\': num == currentpage}" :data-cy="\'inkshopDayPage\' + num" v-bind="$attrs" v-on="$listeners" :id="\'inkshopDayPage\' + num" :style="pageStyle()"><slot></slot></div>',
  // <div class="line" v-if="currentpage > num"></div>
  props:['num', 'currentpage'],
  mounted:function(){
    // console.log("num: " + this.num);
    // console.log("currentpage: " + this.currentpage);
    this.pageOffset = this.num - this.currentpage;
    this.pageOffsetPercent = this.pageOffset * 100;
    // this.$el.innerText = this.content;
  },
  updated: function() {
    // restoreSelection();
  },
  methods:{
    // update: function(event){
    // // saveSelection();
    // console.log(event.target.attributes)
    // console.log(event.target)
    // if( event.target.attributes.object != undefined) {
    //   this.$emit('update', event.target.attributes.object.value, event.target.attributes.object_key.value, event.target.innerText);
    // } else {
    //   this.$emit('update', event.target.attributes.field_name.value, event.target.innerText);
    // }
    // },
    pageStyle: function() {
      // console.log("hiddenStyle")
      // console.log((this.num == this.currentpage))
      var style = "";
      if (this.num <= this.currentpage) {
        style += "display: block; "
      } else {
        style += "display: none; "
      }
      if (this.num == this.currentpage) {
        // style += "margin-bottom: 0; min-height: " + window.innerHeight;
      }
      return style;
    },
    enterPressed: function(event) {
      // event.target.blur();
    }
  }
});
Vue.component('list',{
  template:'<div :data-cy="\'inkshopList_\' + ele_id" v-bind:class="{\'inkshopList\':true, \'big\': big  && big != \'medium\', \'medium\': big == \'medium\', \'bold\': bold, \'bubble\': bubble, \'short\': short, \'has_icon\': icon}" v-bind="$attrs" v-on="$listeners" :style="listStyle()" v-sortable="{ onUpdate: onSort }" :key="component_key" >' +
              '<div v-for="(item, index) in items"  v-bind:class="{\'done\': item.done, \'notdone\': !item.done }" v-if="(hide_first !== true || index != 0)" >' +
              // && ((exclude_finished === false || exclude_finished === true && !item.done) || (exclude_before != undefined && item.done && moment(item.completed_at) >= moment(exclude_before)) || !item.done)
                '<div class="editable_field_area">' +
                '  <span class="prompt bullet" v-if="!bubble && !icon">&bull; </span>' +
                '  <div v-if="icon == \'check\'" class="finished_icon"><i class="fa fa-check"></i></div>' +
                '  <span v-if="bubble" class="button remove" @click="removeItem" :uid="item.uid" :index="index"><i class="fa fa-times"></i></span>' +
                '  <editable :big="big" :bold="bold" :underline="true" :content="item.name" :field_name="index" :index="index"  v-on:keyup.enter="enterPressed"  @update="updateField"></editable>' +
                '  <span v-if="!bubble" class="button remove" @click="removeItem" :uid="item.uid" :index="index"><i class="fa fa-times"></i></span>' +
                '  <div v-if="!item.done && show_excuses && item.workaround != \'\'"> I can {{ item.workaround }} </div>' + 
                '</div>' +
              '</div>' +
              '<div v-bind:class="{\'new_item\': true, \'editable_field_area\':true, \'big\': big  && big != \'medium\', \'medium\': big == \'medium\', \'bold\': bold,}">' +
              '  <span class="prompt bullet "><i v-if="!add_prompt" class="fa fa-plus"></i>' +
              '     <span v-if="items && items.length == 0 && first_prompt">{{first_prompt}}</span> '+
              '     <span v-if="items && items.length != 0 && add_prompt">{{add_prompt}}</span> '+
              '  </span> ' +
              ' <span class="input_wrapper"><input :big="big" :bold="bold" :data-cy="\'inkshopList_\' + ele_id + \'_newListItem\'" v-on:keyup.enter="enterPressedNewItem" @blur="enterPressedNewItem" v-model="newItemName" @update="newItemAdded"  /></span>' +
              // '  <editable :underline="true" v-bind="$attrs" v-on="$listeners" :content="newItemName" :field_name="\'newItemName\'" @update="newItemAdded" v-on:keyup.enter="enterPressedNewItem"></editable>' +
              '</div>' +
            '</div>',
  // <div class="line" v-if="currentpage > num"></div>
  props:['items', 'field_name', 'add_prompt', 'first_prompt', 'hide_first', 'big', 'bold', 'bubble', 'short', 'exclude_finished', 'exclude_before', 'icon', 'component_key', 'show_excuses'],
  mounted:function(){
    this.newItemName = "";
    this.listFieldName = this.field_name;
    this.ele_id = this.field_name.replace(".name", "").replaceAll(".", "_") || false
  },
  watch: {
    items: function(val) {
      if (JSON.stringify(this.items) != JSON.stringify(val)) {
        this.items = val;
        this.renderKey ++;
        this.$root.componentKey += 1
      }
    }
  },
  data: function() {
    return {
      'newItemName': "",
      'ele_id': '',
      'renderKey': 0,
    }
  },
  updated: function() {
    // restoreSelection();

  },
  methods:{
    forceRerender: function() {
      this.renderKey ++;
      this.$root.componentKey += 1;
    },
    updateField: function(index, value){
      // console.log("updateField: list")
      // console.log(index)
      // console.log(value)

      this.items = this.items || [];
      if (this.items[index]) {
        this.items[index] = this.items[index] || {
          "name": value,
          "done": false,
          "queued": false,
          "completed_at": false,
          "excuse": "",
          "workaround": "",
          "uid": inkshop.methods.generateUID(10),
        };
        this.items[index].name = value;
      } else {
        this.items.push({
          "name": value,
          "done": false,
          "queued": false,
          "completed_at": false,
          "excuse": "",
          "workaround": "",
          "uid": inkshop.methods.generateUID(10),
        })
      }
      // saveSelection();
      // console.log(event.target.attributes)
      // console.log(event.target)
      // if( event.target.attributes.object != undefined) {
      //   this.$emit('update', event.target.attributes.object.value, event.target.attributes.object_key.value, event.target.innerText);
      // } else {
      //   this.$emit('update', event.target.attributes.field_name.value, event.target.innerText);
      // }
      this.emitUpdate();
    },
    newItemAdded: function(event) {
      var ele = event.target;
      var value = event.target.value;

      if (value) {
        // console.log("value: " + value)
        // console.log("items: ")
        // console.log(this.items)
        // console.log(this.newItemName)
        this.items = this.items || [];

        this.newItemName = "";
        this.items.push({
          "name": value + "",
          "done": false,
          "queued": false,
          "completed_at": false,
          "excuse": "",
          "workaround": "",
          "uid": inkshop.methods.generateUID(10),
        })
        // console.log("added new item.")
        // console.log(this)
        // console.log(this.items)
        // console.log(this.newItemName)
        // console.log(this)
        // console.log(this.data)
        // this.$set('newItemName', "");
        this.emitUpdate()
        return false;
      }
    },
    enterPressedNewItem: function(event) {
      // console.log("enterPressedNewItem")
      this.newItemAdded(event);
    },
    emitUpdate: function(event) {
      this.$emit('update', this.listFieldName, this.items);
    },
    removeItem: function(event) {
      if (event && event.target && event.target.attributes && event.target.attributes.uid) {
        var target = event.target;
      } else {
        var target = event.target.parentElement;
      }
      // console.log(target);
      // console.log("removeItem: " + target.attributes.index);
      var target_uid = target.attributes.uid.value;
      // console.log(target_uid);
      var new_items = []
      for (var i in this.items) {
        var item_uid = this.items[i].uid;
        // console.log("comparing " + item_uid + " to " + target_uid)
        if (item_uid == target_uid) {
          // console.log("delete this.items[" + i + "]")
          this.items.splice(i, 1);
          // new_items.push(this.items[i]);
        }
      }
      // this.items = new_items;
      this.emitUpdate();
      this.forceRerender();
    },
    listStyle: function() {
      var style = "";
      return style;
    },
    enterPressed: function(event) {
      // console.log("enterPressed")
      event.target.blur();
    },
    onSort: function(event) {
      this.items.splice(event.newIndex, 0, this.items.splice(event.oldIndex, 1)[0]);
      this.emitUpdate();
      this.forceRerender();
      // event.preventDefault();
    }
  }
});
Vue.component('checklist',{
  template:'<div :data-cy="\'inkshopCheckList_\' + ele_id" v-bind:class="{\'inkshopCheckList\':true, }" v-bind="$attrs" v-on="$listeners" :style="listStyle()" v-sortable="{ onUpdate: onSort }" :key="component_key">' +
              '<div v-for="(item, index) in items" v-bind:class="{\'done\': item.done, \'notdone\': !item.done, \'row\': true}"  :data-cy="\'item\' + index">' +
              // v-if="(exclude_finished === false || exclude_finished === true && !item.done) || (exclude_before != undefined && item.done && moment(item.completed_at) >= moment(exclude_before)) || !item.done"
                '<check-button :field_name="index" :content="item.done" @update="itemCheckToggled"></check-button>' + 
                '<div class="editable_field_area">' +
                // '  <span class="prompt bullet">&bull; </span> ' +
                '  <editable :content="item.name" :field_name="index" :index="index"  v-on:keyup.enter="enterPressed"  @update="updateField"></editable>' +
                // '  <span class="button remove" @click="removeItem" :uid="item.uid" :index="index"><i class="fa fa-times"></i></span>' +
                '</div>' +
              '</div>' +
              // '<div class="editable_field_area new_item">' +
              // '  <span class="prompt bullet "><i v-if="!add_prompt" class="fa fa-plus"></i>{{add_prompt}} </span> ' +
              // ' <input v-on:keyup.enter="enterPressedNewItem" @blur="enterPressedNewItem" v-model="newItemName" @update="newItemAdded"  />' +
              // '  <editable :underline="true" v-bind="$attrs" v-on="$listeners" :content="newItemName" :field_name="\'newItemName\'" @update="newItemAdded" v-on:keyup.enter="enterPressedNewItem"></editable>' +
              // '</div>' +
            '</div>',
  // <div class="line" v-if="currentpage > num"></div>
  props:['items', 'field_name', 'add_prompt', 'first_prompt', 'exclude_finished', 'exclude_before', 'disabled', 'component_key'],
  mounted:function(){
    this.newItemName = "";
    this.listFieldName = this.field_name;
    this.ele_id = this.field_name.replace(".name", "").replaceAll(".", "_") || false
  },
  data: function() {
    return {
      'newItemName': "",
      'ele_id': "",
      // 'component_key': 0
    }
  },
  updated: function() {
    // restoreSelection();
  },
  methods:{
    forceRerender() {
      this.$root.componentKey += 1
    },
    updateField: function(index, value){
      this.items = this.items || [];
      if (this.items[index]) {
        this.items[index].name = value;
      } else {
        this.items.push({
          "name": value,
          "done": false,
          "completed_at": false,
          "queued": false,
          "excuse": "",
          "workaround": "",
          "uid": inkshop.methods.generateUID(10),
        })
      }
      // saveSelection();
      // console.log(event.target.attributes)
      // console.log(event.target)
      // if( event.target.attributes.object != undefined) {
      //   this.$emit('update', event.target.attributes.object.value, event.target.attributes.object_key.value, event.target.innerText);
      // } else {
      //   this.$emit('update', event.target.attributes.field_name.value, event.target.innerText);
      // }
      this.emitUpdate();
    },
    itemCheckToggled: function(index, value) {
      // console.log("itemCheckToggled")
      // console.log("disabled: " + this.disabled)
      if (this.disabled) {
        return;
      }
      // console.log("itemCheckToggled")
      // console.log(index)
      // console.log(value)
      // console.log(this.items[index])
      this.items[index].done = !this.items[index].done
      if (this.items[index].done) {
        this.items[index].completed_at = new Date();
      } else {
        this.items[index].completed_at = false;
      }
      this.$emit('update', this.listFieldName, this.items);
    },
    emitUpdate: function(event) {
      if (this.disabled) {
        return;
      }
      // console.log("emitUpdate: " + this.listFieldName)
      // console.log(this.items)
      this.$emit('update', this.listFieldName, this.items);
    },
    listStyle: function() {
      var style = "";
      return style;
    },
    enterPressed: function(event) {
      // console.log("enterPressed")
      event.target.blur();
    },
    onSort: function(event) {
      this.items.splice(event.newIndex, 0, this.items.splice(event.oldIndex, 1)[0]);
      this.emitUpdate();
      this.forceRerender();
    }
  }
});


Vue.component('check-button',{
  template: '<div v-bind:class="{\'active\': content, \'inkshopCheckButton\': true, \'button\': true, \'noTitle\': !title}" @click="update">' +
              '<i class="fa fa-check" v-if="!hideIcon"></i>' +
              '<img v-bind:src="image" v-if="image"/>' +
              '<span class="buttonTitle" v-if="title">{{title}}</span>' +
            '</div>', 
  props:['field_name', 'content', 'title', 'icon', 'image', 'hideIcon'],
  mounted:function(){
    // this.icon = this.icon || "fa fa-check";
  },
  updated: function() {
    // restoreSelection();
  },
  methods:{
    update: function(event){
      // saveSelection();
      // console.log(event)
      // console.log(this.field_name)
      // console.log(this.content)
      this.$emit('update', this.field_name, !this.content);
    },
    enterPressed: function(event) {
      event.target.blur();
    },
    toggleChip: function(event) {

    }
  }
});



Vue.component('star-rating',{
  template: '<div v-bind:class="{\'inkshopStarRating\': true,}" >' +
              '<span v-for="star in stars" @click="setStars(star)" :data-cy="\'star_\' + star">' + 
                '<span class="star checked" v-if="star <= field"><i class="fa fa-star"></i></span>' + 
                '<span class="star unchecked" v-if="star > field || !field"><i class="fa fa-star-o"></i></span>' + 
              '</span>' + 
            '</div>', 
  props:['field_name', 'field', 'icon', 'num_stars'],
  mounted:function(){
    // this.icon = this.icon || "fa fa-check";
    this.num_stars = this.num_stars || 5;
    this.stars = []
    for (var i=1; i<=this.num_stars; i++) {
      this.stars.push(i);
    }
    // console.log("stars:" + this.stars)
  },
  updated: function() {
    // restoreSelection();
  },
  data: function() {
    return {
      'stars': [],
    }
  },
  methods:{
    update: function(event){
      // saveSelection();
      // console.log(event)
      // console.log(this.field_name)
      // console.log(this.field)
      this.$emit('update', this.field_name, !this.field);
    },
    setStars: function(stars) {
      // console.log("setStars")
      // console.log(stars)
      this.field = stars;
      this.$emit('update', this.field_name, this.field);
    },
    enterPressed: function(event) {
      event.target.blur();
    },
    toggleChip: function(event) {

    }
  }
});

Vue.component('toggle-chip',{
  template: '<div class="chip" v-bind:class="{\'active\': field}" @click="update"><i class="material-icons left" v-if="icon">{{icon}}</i><img v-bind:src="image" v-if="image"/>{{title}}</div>', 
  props:['field_name', 'field', 'title', 'icon', 'on', 'image'],
  mounted:function(){
    // console.log(this);
  },
  updated: function() {
    // restoreSelection();
  },
  methods:{
    update: function(event){
      // saveSelection();
      // console.log(event)
      // console.log(this.field_name)
      // console.log(this.field)
      this.$emit('update', this.field_name, !this.field);
    },
    enterPressed: function(event) {
      event.target.blur();
    },
    toggleChip: function(event) {

    }
  }
});
Vue.component('yesnopair',{
  template: '<div class="inkshopYesNoPair"  :data-cy="\'inkshopYesNoPair_\' + ele_id">' + 
                '<span class="title mobile">{{title}}</span>' + 
                '<button data-cy="no" v-bind:class="{\'selected\': field === false}" @click="updateField(false)">{{no_label}}</button> ' + 
                '<button data-cy="yes" v-bind:class="{\'selected\': field === true}" @click="updateField(true)">{{yes_label}}</button>' + 
                '<span class="title desktop">{{title}}</span>' + 
            '</div>', 
  props:['field_name', 'field', 'on', 'yes_text', 'no_text', 'title'],
  computed: {
    yes_label: function() {
      return this.yes_text || "Yes";
    },
    no_label: function() {
      return this.no_text || "No";
    }
  },
  mounted: function() {
    this.ele_id = this.field_name.replace(".name", "").replaceAll(".", "_") || false
  },
  data: function() {
    return {
      'ele_id': '',
    }
  },
  updated: function() {
    // restoreSelection();
  },
  methods:{
    update: function(event){
      // console.log("yesno update:" + this.field_name + " / " + !this.field) 
      this.$emit('update', this.field_name, !this.field);
    },
    enterPressed: function(event) {
      event.target.blur();
    },
    updateField: function(bool) {
      this.$emit('update', this.field_name, bool);
    }
  }
});
Vue.component('rotating',{
  template: '<span class="inkshopRotatingMessage">{{ message }}</span>', 
  props:['messages', 'divider', 'cycle_seconds'],
  computed: {
    
  },
  mounted: function() {
    this.index = -1;
    this.split_divider = (this.divider) ? this.divider : "|";

    this.cycle_seconds = (this.cycle_seconds) ? this.cycle_seconds : 20;
    this.message_list = this.messages.split(this.split_divider);
    this.updateInterval = setInterval(function() {
      this.cycleMessage();
    }.bind(this), this.cycle_seconds * 1000);
    this.cycleMessage();
  },
  data: function() {
    return {
      'message': '',
    }
  },
  updated: function() {
    // restoreSelection();
  },
  methods:{
    cycleMessage: function() {
      this.index += 1;
      if (this.index > this.message_list.length) {
        this.index = 0;
      }
      this.message = this.message_list[this.index];
    }
  }
});
Vue.directive('sortable', {
    inserted: function (el) {
        var sortable = new Sortable(el, options)

        if (this.arg && !this.vm.sortable) {
            this.vm.sortable = {}
        }

        //  Throw an error if the given ID is not unique
        if (this.arg && this.vm.sortable[this.arg]) {
            console.warn('[vue-sortable] cannot set already defined sortable id: \'' + this.arg + '\'')
        } else if( this.arg ) {
            this.vm.sortable[this.arg] = sortable
        }
    },
    bind: function (el, binding) {
        this.options = binding.value || {};
    }
})
Vue.filter('round', function(value) {
  return Math.round(value);
});
Vue.filter('capfirst', function(value) {
  if (value) {
    return value.substring(0,1).toUpperCase() + value.substring(1, value.length);
  }
  return ""
});