require 'rails_helper'

RSpec.describe SectionsController, type: :routing do
  describe 'routing' do

    it 'routes to #index' do
      expect(:get => '/sections').to route_to('sections#index')
    end

    it 'routes to #show' do
      expect(:get => '/sections/1').to route_to('sections#show', :id => '1')
    end
  end
end
