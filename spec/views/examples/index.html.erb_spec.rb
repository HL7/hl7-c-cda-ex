require 'rails_helper'

RSpec.describe 'examples/index', type: :view do
  before(:each) do
    sect = FactoryGirl.create(:section)
    assign(:examples, FactoryGirl.create_list(:example, 2, section: sect))
  end

  it 'renders a list of examples' do
    render
    assert_select 'tr>td>p', :text => 'The-Example'.to_s, :count => 2
    assert_select 'tr>td>p', :text => 'Comment-comment'.to_s, :count => 2
    assert_select 'tr>td', :text => 'download details'.to_s, :count => 2
  end
end
