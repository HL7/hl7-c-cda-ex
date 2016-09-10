require 'rails_helper'

RSpec.describe ExamplesController, type: :routing do
  describe 'routing' do

    it 'routes to #index' do
      expect(:get => '/examples').to route_to('examples#index')
    end

    it 'routes to #show' do
      expect(:get => '/examples/1').to route_to('examples#show', :id => '1')
    end
  end
end
