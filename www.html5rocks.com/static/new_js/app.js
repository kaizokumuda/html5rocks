$('#search_show').click(function(){
  $('.subheader.features').hide();
  $('#features_show').removeClass('active');
  $('#search_show').addClass('active');
  $('.subheader.search').show();
  $('#q').focus();
});

$('#search_hide').click(function(){
  $('.subheader.search').hide();
});

$('#features_show').click(function(){
  $('.subheader.search').hide();
  $('#search_show').removeClass('active');
  $('#features_show').addClass('active');
  $('.subheader.features').show();
});

$('#features_hide').click(function(){
  $('#features_show').removeClass('active');
  $('.subheader.features').hide();
});