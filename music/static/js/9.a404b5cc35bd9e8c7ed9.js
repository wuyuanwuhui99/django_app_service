webpackJsonp([9],{HStV:function(t,s,i){"use strict";Object.defineProperty(s,"__esModule",{value:!0});var n=i("Dd8w"),e=i.n(n),a=i("qwAB"),o=i("ZV4u"),r=i("PvFA"),d=i("y/jF"),l=i("mtWM"),h=i.n(l);var c=i("NYxO"),u={mixins:[i("F4+m").b],data:function(){return{douyinList:[],hasCommit:!1,showLoading:!1}},methods:e()({handlePlaylist:function(t){var s=t.length>0?"60px":"";this.$refs.listWrapper.style.bottom=s,this.$refs.douyinList&&this.$refs.douyinList.refresh(),this.$refs.playList&&this.$refs.playList.refresh()},selectSong:function(t,s){this.hasCommit||(this.orderPlay({list:this.douyinList,index:s}),this.hasCommit=!0),this.insertSong({song:new r.b(t),index:s})},random:function(){var t=this.douyinList;0!==t.length&&(t=t.map(function(t){return new r.b(t)}))}},Object(c.b)(["insertSong","randomPlay","orderPlay"])),components:{Scroll:a.a,SongList:o.a,loading:d.a},mounted:function(){var t=this;this.showLoading=!0,h.a.get("/service/music/getDouyinList/").then(function(s){t.showLoading=!1,t.douyinList=s.data.data}),this.$nextTick(function(){t.handlePlaylist(t.douyinList)})}},f={render:function(){var t=this.$createElement,s=this._self._c||t;return s("transition",{attrs:{name:"slide"}},[s("div",{staticClass:"douyin"},[s("div",{ref:"listWrapper",staticClass:"list-wrapper"},[s("scroll",{ref:"douyinList",staticClass:"list-scroll",attrs:{data:this.douyinList}},[s("div",{staticClass:"list-inner"},[s("song-list",{attrs:{songs:this.douyinList},on:{select:this.selectSong}})],1)]),this._v(" "),s("div",{directives:[{name:"show",rawName:"v-show",value:this.showLoading,expression:"showLoading"}],staticClass:"loading-container"},[s("loading")],1)],1)])])},staticRenderFns:[]};var y=i("VU/8")(u,f,!1,function(t){i("a1KZ")},"data-v-2c52d862",null);s.default=y.exports},a1KZ:function(t,s){}});
//# sourceMappingURL=9.a404b5cc35bd9e8c7ed9.js.map