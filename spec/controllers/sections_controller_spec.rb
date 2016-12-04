require 'rails_helper'

RSpec.describe SectionsController, type: :controller do
  let(:section) { FactoryGirl.create(:section) }

  describe 'GET #index' do
    it 'assigns all sections as @sections' do
      get :index, {}
      expect(assigns(:sections)).to eq([section])
    end
  end

  describe 'GET #show' do
    it 'assigns the requested section as @section' do
      get :show, {:id => section.to_param}
      expect(assigns(:section)).to eq(section)
    end
  end
end
