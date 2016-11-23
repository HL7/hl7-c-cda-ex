class Api::RepositoryController < ApplicationController
  skip_before_filter :verify_authenticity_token

  def create
    if params.include?('ref') && params['ref'] == 'refs/heads/master'
      if params.include?('head_commit')
        message = params['head_commit'].include?('message') ? params['head_commit']['message'] : nil
        model = RepoMessage.new(action: request.headers['HTTP_X_GITHUB_EVENT'],
                                description: message, body: params['head_commit'].to_s,
                                status: 'recd')
      else
        model = RepoMessage.new(action: request.headers['HTTP_X_GITHUB_EVENT'],
                                body: params.to_s, status: 'unk')
      end
      model.save!
    end
    render text: 'OK'
  end
end
