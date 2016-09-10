require 'rails_helper'

RSpec.describe 'sections/index', type: :view do
  before(:each) do
    assign(:sections, FactoryGirl.create_list(:section, 2))
    #        [
    #   Section.create!(
    #     :name => 'Name',
    #     :type => 'Type',
    #     :narrative => 'MyText'
    #   ),
    #   Section.create!(
    #     :name => 'Name',
    #     :type => 'Type',
    #     :narrative => 'MyText'
    #   )
    # ])
  end

  it 'renders a list of sections' do
    render
    assert_select 'tr>td', text: 'Name'.to_s, count: 2
    assert_select 'tr>td', text: 'Type'.to_s, count: 2
    assert_select 'tr>td', text: 'MyText'.to_s, count: 2
  end
end
