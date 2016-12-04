require 'rails_helper'

RSpec.describe 'examples/show', type: :view do
  before(:each) do
    sect = FactoryGirl.create(:section)
    @example = assign(:example, FactoryGirl.create(:example, section: sect))
  end

  it 'renders attributes in <p>' do
    render
    # expect(rendered).to match(/Allergies and Intolerances/)
    expect(rendered).to match(/The-Example/)
    expect(rendered).to match(/Comments/)
    expect(rendered).to match(/Custodian/)
    expect(rendered).to match(/SITE C-CDA Validator/)
  end
end
