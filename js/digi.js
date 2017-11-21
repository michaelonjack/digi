if (typeof jQuery === 'undefined') {
	throw new Error('JavaScript requires jQuery')
}

/*
function loadMoviePosters() {

	jQuery('.poster-container a img').each( function(index) {
		var currentImage = jQuery(this);
		var title = currentImage.attr('movie-title').trim();
		var endpoint = 'https://api.themoviedb.org/3/search/movie?api_key=f8bacc22524d435a1476adae350b4d41&query=' + title;

		jQuery.getJSON(endpoint, function(json) {
			if (json.results.length > 0) {
				currentImage.attr('src', 'https://image.tmdb.org/t/p/w500/' + json.results[0].poster_path);
			} else {
				currentImage.attr('src', '/images/placeholder.jpg');
			}
		});
	});
}
*/


/*
	Set the movie title and other hidden inputs when a poster is clicked on the Post Code page
*/
function setSelectedMovie() { 
	jQuery('.movie-link').click(function() { 
		var poster = jQuery(this).find('.poster-med');

		jQuery('#form-movie-id').val(poster.attr('movie-id'));
		jQuery('#form-poster-url').val(poster.attr('poster-url'));
		jQuery('#form-backdrop-url').val(poster.attr('backdrop-url'));
		jQuery('#form-movie-title').val(poster.attr('movie-title'));
		jQuery('#form-season').val(poster.attr('season'));

		jQuery('#form-row').show();
	});
}



/*
	Initalizes the search bar to send out AJAX request with each key stroke
	Initializes both the nav search bar and the post code search bar
*/
function initSearchbar() { 
	jQuery('#results').hide();
	jQuery('#form-row').hide();

	/*
		This is for the search bar on the Post Code page
		It uses the MovieDB database to return results to the user
	*/
	if (jQuery('#movie').length > 0) { 
		jQuery('#movie').keyup(function() { 
			var query = jQuery('#movie').val();

			var endpoint = '';
			if ( jQuery('#movie-option').is(':checked') ) {
				endpoint = 'https://api.themoviedb.org/3/search/movie?api_key=f8bacc22524d435a1476adae350b4d41&query=' + query;
			}
			else if ( jQuery('#television-option').is(':checked') ) {
				endpoint = 'https://api.themoviedb.org/3/search/tv?api_key=f8bacc22524d435a1476adae350b4d41&query=' + query;
				// Take the #1 result from the search and create a request for the show to display seasons
				jQuery.ajax({
					url: endpoint,
					async: false
				}).done(function (json) {
					if (json.results.length > 0) {
						var tv_id = json.results[0].id;
						endpoint = 'https://api.themoviedb.org/3/tv/' + tv_id + '?api_key=f8bacc22524d435a1476adae350b4d41';
					}
				});
			}
			
			if (query.length > 0) {

				jQuery.getJSON(endpoint, function(json) { 
					
					jQuery('.poster-container a img').each( function(index) { 
						if (json.results && json.results.length >= index + 1) { 
							var result = json.results[index];
							
							jQuery(this).closest('.poster-column').show();
							if (result.poster_path) {

								// Set the attributes for the images in the Results row
								jQuery(this).attr('movie-id', result.id);
								jQuery(this).attr('poster-url', result.poster_path);
								jQuery(this).attr('backdrop-url', result.backdrop_path);
								jQuery(this).attr('src', 'https://image.tmdb.org/t/p/w500/' + result.poster_path);

								if( jQuery('#movie-option').is(':checked') ) {
									jQuery(this).attr('movie-title', result.title);
									jQuery(this).siblings().find('.poster-title').text(result.title);
									jQuery(this).attr('season', '-1');
								}
								else if( jQuery('#collection-option').is(':checked') ) {
									jQuery(this).attr('movie-title', result.name);
									jQuery(this).siblings().find('.poster-title').text(result.name);
								}
							} else { 
								// If the image couldn't be loaded, remove the column from the results
								jQuery(this).closest('.poster-column').hide();
							}
						}

						// Is the search item a tv show? Then display the first result's seasons
						else if (json.seasons && json.seasons.length >= index + 1) {
							var season = json.seasons[index];

							jQuery(this).closest('.poster-column').show();
							if (season.poster_path) {

								jQuery(this).attr('movie-id', json.id);
								jQuery(this).attr('poster-url', season.poster_path);
								jQuery(this).attr('backdrop-url', json.backdrop_path);
								jQuery(this).attr('src', 'https://image.tmdb.org/t/p/w500/' + season.poster_path);
								jQuery(this).attr('season', season.season_number);
								if(season.season_number === 0) {
									jQuery(this).attr('movie-title', json.name + ' Complete');
									jQuery(this).siblings().find('.poster-title').text(json.name + ' Complete');
								} else {
									jQuery(this).attr('movie-title', json.name + ' Season ' + season.season_number);
									jQuery(this).siblings().find('.poster-title').text(json.name + ' Season ' + season.season_number);
								}
							} else {
								// If the image couldn't be loaded, remove the column from the results
								jQuery(this).closest('.poster-column').hide();
							}
						}
					});

					// Once the results have been loaded, hide any empty columns
					jQuery('.poster-med[poster-url=""]').each(function() {
						jQuery(this).closest('.poster-column').hide();
					})

					// Display the results!
					jQuery('#results').show();
				});

			} else { 
				// Search bar is empty, hide the Results div
				jQuery('#results').hide();
			}
		});
	}

	/*
		This is for the search bar in nav bar of most pages
		It uses the site's ndb database to search among the movies that currently exist on the site
		These should probably be in two separate function but..meh..
	*/
	if(jQuery('#movie-search').length > 0) {
		var request = null;
		jQuery('#movie-search').keyup(/*jQuery.debounce(0,*/ function() { 
			var query = jQuery('#movie-search').val();
			var endpoint = '/ajaxcodesearch?q=' + query;
			
			var searchResults = [];
			jQuery('#movie-search').autocomplete({source: searchResults});
			if (query.length > 0) {

				request = jQuery.getJSON(endpoint, function(json) {
				
					for (var i=0; i<10 && i<json.results.length; i++) { 
						var result = json.results[i].title;
						searchResults.push({label:result, value:result});
					}
				
					jQuery('#movie-search').autocomplete({source: searchResults});
				});
			} 
		});
	}
}


/*
	Presents a confirmation modal when user clicks to send a message
	The modal provides details on how the message with be sent and gives action choices (Send/Cancel)
*/
function validateMessageForm() { 
	if (jQuery("#messageform").length) {
		jQuery("#messageform").validate({
		    submitHandler: function (form) {
		        jQuery("#confirmModal").modal('show');
		        jQuery('#sendBtn').click(function () {
		            form.submit();
		       });
		    }
		});
	}
}



/*
	(Not currently doing anything I don't think)
	Will present confirmation modal when user is submiting a code for sale
*/
function validateCodeForm() { 
	if (jQuery("#action-button").length) {
		jQuery("#action-button").validate({
		    submitHandler: function (form) {
		        jQuery("#confirmModal").modal('show');
		        jQuery('#sendBtn').click(function () {
		            form.submit();
		       });
		    }
		});
	}
}



/*
	Set the details of the movie on the Code page
	Uses MovieDB to get the trailer URL, synopsis, runtime, release date, etc.
*/
function setCodeDetails() { 
	if (jQuery("#details-trailer").length > 0) { 
		jQuery("#details-trailer").hide();

		var movieid = jQuery("body").attr("movieid");
		var code_type = jQuery("#code-type").attr("value");
		code_type = code_type === '1' ? 'movie' : 'tv';

		var imdb_base_url = "https://www.imdb.com/title/";
		var rotten_base_url = "https://www.rottentomatoes.com/m/";
		var video_base_url = "https://www.youtube.com/embed/";
		var video_options = "?modestbranding=1&autohide=1&showinfo=0&controls=0";

		var video_endpoint = '';
		var info_endpoint = '';
		if (code_type === 'movie') {
			video_endpoint = "https://api.themoviedb.org/3/movie/" + movieid + "/videos?api_key=f8bacc22524d435a1476adae350b4d41&language=en-US";
			info_endpoint = "https://api.themoviedb.org/3/movie/" + movieid + "?api_key=f8bacc22524d435a1476adae350b4d41&language=en-US";
		}
		else if (code_type === 'tv') {
			video_endpoint = "https://api.themoviedb.org/3/tv/" + movieid + "/videos?api_key=f8bacc22524d435a1476adae350b4d41&language=en-US";
			info_endpoint = "https://api.themoviedb.org/3/tv/" + movieid + "?api_key=f8bacc22524d435a1476adae350b4d41&language=en-US";
		}

		jQuery.getJSON(video_endpoint, function(json) { 

			if (json.results.length > 0) {
				var video_key = json.results[0].key;
				jQuery('#details-trailer').attr('src', video_base_url + video_key + video_options);
				
				jQuery('#details-trailer').show();
			}
		});

		jQuery.getJSON(info_endpoint, function(json) { 
			
			if (json) {
				
				jQuery('#details-synopsis').text(json.overview);
				if (code_type === 'tv') {
					var season_num = parseInt( jQuery('#season').attr('value') );
					
					var season = '';
					for(var i=0; i<json.seasons.length; i++) {
						if (json.seasons[i].season_number === season_num) {
							season = json.seasons[i];
							break;
						}
					}

					if (season_num !== 0) {
						jQuery('#details-runtime').text(season.episode_count.toString() + " episodes");
						jQuery('#details-release').text(new Date(season.air_date).toDateString());
					} else {
						// We'll consider season 0 = Complete series
						jQuery('#details-runtime').text(json.seasons.length.toString() + " seasons");
						jQuery('#details-release').text(new Date(json.first_air_date).toDateString());
					}
					jQuery('#imdb-link').css({'opacity':'0.2', 'pointer-events':'none'});
					jQuery('#rotten-link').css({'opacity':'0.2', 'pointer-events':'none'});
				} else {
					jQuery('#details-runtime').text(json.runtime + " minutes");
					jQuery('#details-release').text(new Date(json.release_date).toDateString());
					jQuery('#imdb-link').attr('href', imdb_base_url + json.imdb_id);
					jQuery('#rotten-link').attr('href', rotten_base_url + json.title.replace(/[ ·-]/g, "_").replace(/[:'.,!?]/g, ""));
				}
			}
		});
	}
}


/*

*/
function initCodeTypeRadio() {
	jQuery('input[type=radio][name="code-type"]').change( function() {
		jQuery('#results').hide();
		jQuery('#movie').val('');
		jQuery('#form-row').hide();

		if (jQuery(this).attr('id') === 'movie-option') {
			jQuery('#movie').attr('placeholder', 'search for a movie');
			jQuery('#form-type').val("1");
		}
		else if (jQuery(this).attr('id') === 'television-option') {
			jQuery('#movie').attr('placeholder', 'search for a tv show');
			jQuery('#form-type').val("2");
		}
		/*
		else if (jQuery(this).attr('id') === 'collection-option') {
			jQuery('#movie').attr('placeholder', 'search for a collection');
			jQuery('#form-type').val("3");
		}
		*/
	});
}



/*
	Initializes the "Load More" button on the Code listing page
	Clicking this button will dynamically load more codes on the page without refreshing
*/
var page = 1;
function initLoadMoreButton() {
	if ( jQuery('#loadMoreBtn').length < 1 ) {
		return;
	}

	var format = jQuery('#codeFormat').attr('format');
	var sort = jQuery('#sort-options').val();

	// 16 is the maximum number of codes per page
	// If there are less than 16 on the page then there are no more codes to load so remove the button
	if (jQuery('.poster-container').length < 16*page ) {
		jQuery('#loadMoreBtn').remove();
		return;
	}

	jQuery('#loadMoreBtn').click(function() {
		page += 1;
		jQuery.getJSON('/ajaxgetnextpage?page=' + page.toString() + '&format=' + format + '&sort=' + sort, function(json) {
			jQuery.each(json.results, function(index) {
				var currCode = json.results[index];
				var newCodeHTML = "";
				newCodeHTML += "<div class='col-xs-6 col-md-3 text-center'>";
				newCodeHTML += "	<div class='poster-container'>";
				newCodeHTML += "		<a href='/code?id=" + currCode.id + "' class='darken hover'>";
				newCodeHTML += "			<img src='https://image.tmdb.org/t/p/w342/" + currCode.posterurl + "' class='img-responsive poster-med' movie-title='" + currCode.title + "'>";
				newCodeHTML += "			<div class='poster-title-container'>";
				newCodeHTML += "				<div class='poster-title'>";
				newCodeHTML += "					" + currCode.title + "<br>$" + parseFloat(currCode.price).toFixed(2).toString();
				newCodeHTML += "				</div>";
				newCodeHTML += "			</div>";
				newCodeHTML += "		</a>";
				newCodeHTML += "	</div>";
				newCodeHTML += "</div>";

				jQuery('.col-xs-6.col-md-3.text-center').last().after(newCodeHTML);
			});

			if (jQuery('.poster-container').length < 16*page ) {
				jQuery('#loadMoreBtn').remove();
			}
		});
	});
}




/*
	Initializes the Sort By selection box
	This will reload the page with the newly selected sorting options
*/
function initSortOptionsSelect() { 
	if( jQuery('#sort-options').length > 0 ) {
		jQuery('#sort-options').change(function() {
			var option = jQuery(this).val();
			var format = jQuery('#codeFormat').attr('format');

			window.location.href = "/allcodes?format=" + format + "&page=1&sort=" + option;
		});
	}
}






jQuery(document).ready( function() {

	// Allows mobile users to simulate the hover effect by touching
	jQuery('.hover').bind('touchstart touchend', function(e) {
        jQuery(this).toggleClass('hover_effect');
    });

    jQuery('#form-code').tooltip({
    	'trigger': 'focus',
    	'title': 'By entering your code now it will automatically be emailed to the buyer after payment is sent. '
    				+ 'If you do not enter your code now, you will need to manually send the code to the buyer after '
    				+ 'payment is received.'
    });

	initSearchbar();
	initCodeTypeRadio();
	initLoadMoreButton();
	initSortOptionsSelect();
	setSelectedMovie();
	setCodeDetails();
	validateMessageForm();
	validateCodeForm();

});