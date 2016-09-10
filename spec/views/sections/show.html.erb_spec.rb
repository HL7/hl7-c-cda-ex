require 'rails_helper'

RSpec.describe 'sections/show', type: :view do
  before(:each) do
    @section = assign(:section, FactoryGirl.create(:section))
  end

  it 'renders attributes in <p>' do
    render
    expect(rendered).to match(/Name/)
    expect(rendered).to match(/Type/)
    expect(rendered).to match(/MyText/)
  end
end
