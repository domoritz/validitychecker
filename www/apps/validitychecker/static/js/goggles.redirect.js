/* Author: 
   Dominik Moritz
   */

Goggles.redirect = (function() {
	query = ''

	function init() {
		$('input[type=submit]').click(function(){

			var query = encodeURI($('#query').val())
			console.log(query)
			check(query)

			return false;
		})
	}

	function check(query) {
		$.ajax({
			url:'/status/'+query,
			dataType: 'json',
			success: function (data, textStatus, xhr) {
				console.log(data.status);
				if (data.status == 'Finished') {
					window.location.href = data.resulturl;
				} else if (data.status in {'Queued':1, 'Invalid':1, 'Unknown':1}) {
					window.setTimeout(function () {
						check(query);
					}, 1000);
				}
			}
		});
	}

	/*********************
	 * API Functions
	 * *******************/
	return {
		init : init,
	};
})();






















