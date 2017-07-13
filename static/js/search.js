$("#search-form").on("submit",){
  var query = {};
  var searchTerms = $("#search_search_text").val();
  var filterByApproval = $("[name=approvalFilter]:checked").val();
  var certification = $("[name=certificationFilter]:checked").val();
  query.approval = filterByApproval == '' ? '' : filterByApproval;
  query.searchTerms = searchTerms == '' ? '' : searchTerms;
  query.certification = certification == '' ? '' : certification;

  $.ajax({
      url: "/search",
      method: post
      contentType: json,
      data: query}
      :
    )

}
