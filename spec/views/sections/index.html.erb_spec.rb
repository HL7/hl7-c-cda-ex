require 'rails_helper'

RSpec.describe 'sections/index', type: :view do
  before(:each) do
    assign(:sections, FactoryGirl.create_list(:section, 2))
  end

  it 'renders a list of sections' do
    render
    assert_select 'tr>td', text: /Allergies and Intolerances/, count: 2
    assert_select 'tr>td>div>a', text: /section examples }/i, count: 2
  end
end
