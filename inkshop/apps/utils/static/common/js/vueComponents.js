Vue.component('editable',{
  template:'<span :id=\'ele_id\' :data-cy="ele_id" v-bind:class="{ \'editable_field\': true, \'big\': big  && big != \'medium\', \'medium\': big == \'medium\', \'bold\': bold, \'underline\': underline }" contenteditable="true" @blur="update" v-html="content" v-on:keyup.enter="enterPressed"  v-on:keyup="keyUp"></span>',
  props:['content', 'big', 'bold', 'underline', 'enter_focus', 'multiline'],
  mounted:function(){
    // console.log("editable mounted()")
    this.$el.innerText = this.content;
    this.lastUpdatedValue = this.$el.innerText
    this.ele_id = this.$el.attributes.field_name.value.replace(".name", "").replaceAll(".", "_") || false
  },
  data: function() {
    return {
      'ele_id': 'blank',
    }
  },
  updated: function() {
    // restoreSelection();
    // console.log(this.$el)
    // console.log("editable updated(" + this.content + ")")
    this.$el.innerText = this.content;
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
    enterPressed: function(event) {
      try {
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
    keyUp: function(event) {
      try {
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
      } catch {}
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
    //   // saveSelection();
    //   console.log(event.target.attributes)
    //   console.log(event.target)
    //   if( event.target.attributes.object != undefined) {
    //     this.$emit('update', event.target.attributes.object.value, event.target.attributes.object_key.value, event.target.innerText);
    //   } else {
    //     this.$emit('update', event.target.attributes.field_name.value, event.target.innerText);
    //   }
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
  template:'<div :data-cy="\'inkshopList_\' + ele_id" v-bind:class="{\'inkshopList\':true, }" v-bind="$attrs" v-on="$listeners" :style="listStyle()" >' +
              '<div v-for="(item, index) in items"  v-if="hide_first !== true || index != 0">' +
                '<div class="editable_field_area">' +
                '  <span class="prompt bullet">&bull; </span> ' +
                '  <editable :underline="true" :content="item.name" :field_name="index" :index="index"  v-on:keyup.enter="enterPressed"  @update="updateField"></editable>' +
                '  <span class="button remove" @click="removeItem" :uid="item.uid" :index="index"><i class="fa fa-times"></i></span>' +
                '</div>' +
              '</div>' +
              '<div class="editable_field_area new_item">' +
              '  <span class="prompt bullet "><i v-if="!add_prompt" class="fa fa-plus"></i>' +
              '     <span v-if="items && items.length == 0 && first_prompt">{{first_prompt}}</span> '+
              '     <span v-if="items && items.length != 0 && add_prompt">{{add_prompt}}</span> '+
              '  </span> ' +
              ' <input :data-cy="\'inkshopList_\' + ele_id + \'_newListItem\'" v-on:keyup.enter="enterPressedNewItem" @blur="enterPressedNewItem" v-model="newItemName" @update="newItemAdded"  />' +
              // '  <editable :underline="true" v-bind="$attrs" v-on="$listeners" :content="newItemName" :field_name="\'newItemName\'" @update="newItemAdded" v-on:keyup.enter="enterPressedNewItem"></editable>' +
              '</div>' +
            '</div>',
  // <div class="line" v-if="currentpage > num"></div>
  props:['items', 'field_name', 'add_prompt', 'first_prompt', 'hide_first'],
  mounted:function(){
    this.newItemName = "";
    this.listFieldName = this.field_name;
    this.ele_id = this.field_name.replace(".name", "").replaceAll(".", "_") || false
  },
  data: function() {
    return {
      'newItemName': "",
      'ele_id': '',
    }
  },
  updated: function() {
    // restoreSelection();
  },
  methods:{
    updateField: function(uid, value){
      // console.log("update: list")
      // console.log(index)
      // console.log(value)

      this.items = this.items || [];
      if (this.items[index]) {
        this.items[index] = this.items[index] || {
          "name": value,
          "done": false,
          "queued": false,
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
      console.log(event);
      var ele = event.target;
      var value = event.target.value;

      if (value) {
        // console.log("newItemAdded")
        // console.log("value: " + value)
        // console.log("items: ")
        // console.log(this.items)
        // console.log(this.newItemName)
        this.newItemName = "";
        this.items.push({
          "name": value + "",
          "done": false,
          "queued": false,
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
      // console.log("emitUpdate: " + this.listFieldName)
      // console.log(this.items)
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
    },
    listStyle: function() {
      var style = "";
      return style;
    },
    enterPressed: function(event) {
      // console.log("enterPressed")
      event.target.blur();
    }
  }
});
Vue.component('checklist',{
  template:'<div :data-cy="\'inkshopCheckList_\' + ele_id" v-bind:class="{\'inkshopCheckList\':true, }" v-bind="$attrs" v-on="$listeners" :style="listStyle()" >' +
              '<div v-for="(item, index) in items" v-bind:class="{\'done\': item.done, \'row\': true}"  :data-cy="\'item\' + index">' +
                '<check-button :field_name="index" :content="item.done" title="Done" @update="itemCheckToggled"></check-button>' + 
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
  props:['items', 'field_name', 'add_prompt', 'first_prompt', 'disabled'],
  mounted:function(){
    this.newItemName = "";
    this.listFieldName = this.field_name;
    this.ele_id = this.field_name.replace(".name", "").replaceAll(".", "_") || false
  },
  data: function() {
    return {
      'newItemName': "",
      'ele_id': "",
    }
  },
  updated: function() {
    // restoreSelection();
  },
  methods:{
    updateField: function(index, value){
      // console.log("update: list")
      // console.log(index)
      // console.log(value)

      this.items = this.items || [];
      if (this.items[index]) {
        this.items[index].name = value;
      } else {
        this.items.push({
          "name": value,
          "done": false,
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
    }
  }
});


Vue.component('check-button',{
  template: '<div v-bind:class="{\'active\': content, \'inkshopCheckButton\': true, \'button\': true}" @click="update">' +
              '<i class="fa fa-check" v-if="!hideIcon"></i>' +
              '<img v-bind:src="image" v-if="image"/>' +
              '<span class="buttonTitle">{{title}}</span>' +
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
    console.log("stars:" + this.stars)
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
      console.log("setStars")
      console.log(stars)
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
                '<button data-cy="no" v-bind:class="{\'selected\': field === false}" @click="updateField(false)">{{no_label}}</button> ' + 
                '<button data-cy="yes" v-bind:class="{\'selected\': field === true}" @click="updateField(true)">{{yes_label}}</button>' + 
                '<span class="title">{{title}}</span>' + 
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
      console.log("yesno update:" + this.field_name + " / " + !this.field) 
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

Vue.directive('sortable', {
      inserted: function (el, binding) {
      var sortable = new Sortable(el, binding.value || {});
      }
  });
Vue.filter('round', function(value) {
  return Math.round(value);
});
Vue.filter('capfirst', function(value) {
  return value.substring(0,1).toUpperCase() + value.substring(1, value.length);
});