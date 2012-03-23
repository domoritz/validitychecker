/* Author: 
   Dominik Moritz
   */

Goggles.redirect = (function() {
	query = '';

	function init() {
		$('#errorwrapper').hide();

		$('input[type=submit].search').click(function(){

			$('#errorwrapper').slideUp();

			var query = encodeURI($('#query').val());
			console.log(query);
			check(query);

			return false;
		});

		$('.close').click(function(){
			$('#errorwrapper').slideUp('fast');
		});

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
					}, 2500);
				} else {
					// error...
					$('#errorwrapper').slideDown().find('.more').html("<strong>"+data.error+ "</strong> " + data.message);
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






















