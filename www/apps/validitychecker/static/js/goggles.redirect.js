/* Author: 
   Dominik Moritz
   */

Goggles.redirect = (function() {
	query = ''

	function init() {
		$('input[type=submit].search').click(function(){

			var query = encodeURI($('#query').val())
			console.log(query)
			check(query)

			return false;
		})
	}

	function check(query) {
		$('#query').addClass('working');
		$.ajax({
			url:'/status/'+query,
			dataType: 'json',
			success: function (data, textStatus, xhr) {
				console.log(data.status);
				if (data.status == 'SUCCESS') {
					window.location.href = data.resulturl;
				} else if (data.status in {'PENDING':1, 'STARTED':1, 'RETRY':1}) {
					window.setTimeout(function () {
						check(query);
					}, 1000);
				} else {
					// error...
					$('#query').removeClass('working');
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






















