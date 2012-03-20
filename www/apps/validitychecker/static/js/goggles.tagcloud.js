/* Author: 

*/

Goggles.tagcloud = (function() {
	function init() {
		$(".home .popular ul").tagcloud({
			type:"list", 
			sizemin:16, 
			sizemax:30, 
			colormin:"aaa", 
			colormax:"888"
		});
	}

	/*********************
	 * API Functions
	 * *******************/
	return {
		init : init,
	};
})();

