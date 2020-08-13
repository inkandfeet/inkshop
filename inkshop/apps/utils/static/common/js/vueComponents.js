Vue.component('editable',{
  template:'<span class="editable_field" contenteditable="true" @blur="update" v-html="content" v-on:keyup.enter="enterPressed"></span>',
  props:['content'],
  mounted:function(){
    this.$el.innerText = this.content;
  },
  updated: function() {
    // restoreSelection();
  },
  methods:{
    update: function(event){
      // saveSelection();
      this.$emit('update', event.target.attributes.field_name.value, event.target.innerText);
    },
    enterPressed: function(event) {
      event.target.blur();
    }
  }
});

Vue.component('toggle-chip',{
  template: '<div class="chip" v-bind:class="{\'active\': field}" @click="update"><i class="material-icons left" v-if="icon">{{icon}}</i><img v-bind:src="image" v-if="image"/>{{title}}</div>', 
  props:['field_name', 'field', 'title', 'icon', 'on', 'image'],
  mounted:function(){
    console.log(this);
  },
  updated: function() {
    // restoreSelection();
  },
  methods:{
    update: function(event){
      // saveSelection();
      console.log(event)
      console.log(this.field_name)
      console.log(this.field)
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
  template: '<div><a class="waves-effect btn-flat cyan lighten-5 toggleable_button" v-bind:class="{\'selected\': field === false}" @click="updateField(false)">{{no_label}}</a> <a class="waves-effect btn-flat cyan lighten-5 toggleable_button" v-bind:class="{\'selected\': field === true}" @click="updateField(true)">{{yes_label}}</a></div>', 
  props:['field_name', 'field', 'on', 'yes_text', 'no_text'],
  computed: {
    yes_label: function() {
      return this.yes_text || "Yes";
    },
    no_label: function() {
      return this.no_text || "No";
    }
  },
  updated: function() {
    // restoreSelection();
  },
  methods:{
    update: function(event){
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