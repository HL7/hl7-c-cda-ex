class Api::RepositoryController < ApplicationController
  skip_before_filter :verify_authenticity_token

  def create
    model = RepoMessage.new(action: request.headers['HTTP_X_GitHub_Event'], body: params.to_s)
    model.save!
    render text: 'OK'
  end
end
