class Api::RepositoryController < ApplicationController
  skip_before_filter :verify_authenticity_token

  def create
    if params.include?('ref') && params['ref'] == 'refs/heads/master'
      source = params.include?('repository') && params['repository'].include?('full_name') ?
          params['repository']['full_name'] : nil
      if params.include?('head_commit')
        model = RepoMessage.build_from_commit_message(request.headers['HTTP_X_GITHUB_EVENT'],
                                                      'recd', params['head_commit'],
                                                      source)
      else
        model = RepoMessage.new(action: request.headers['HTTP_X_GITHUB_EVENT'],
                                body: params.to_s, status: 'unk', repo_source: source)
      end
      model.save!
      GitUpdate.process!(model)
    end
    render text: 'OK'
  end
end
