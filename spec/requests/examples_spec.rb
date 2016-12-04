require 'rails_helper'

RSpec.describe 'Examples', type: :request do
  describe 'GET /examples' do
    it 'works! (now write some real specs)' do
      get examples_path
      expect(response).to have_http_status(200)
    end
  end
end
