require 'rails_helper'

RSpec.describe ExamplesController, type: :controller do
  let(:example) { FactoryGirl.create(:example, section: FactoryGirl.build(:section)) }

  describe 'GET #index' do
    it 'assigns all examples as @examples' do
      get :index, {}
      expect(assigns(:examples)).to eq([example])
    end
  end

  describe 'GET #show' do
    it 'assigns the requested example as @example' do
      get :show, {:id => example.to_param}
      expect(assigns(:example)).to eq(example)
    end
  end
end
