require 'rails_helper'

RSpec.describe "examples/show", type: :view do
  before(:each) do
    @example = assign(:example, Example.create!(
      :name => "Name",
      :comments => "Comments",
      :customdian => "Customdian",
      :validation => "Validation",
      :keywords => "Keywords",
      :full_sample => "Full Sample",
      :status => "Status",
      :example => "MyText",
      :committee => "Committee",
      :approved => false,
      :comment => "MyText"
    ))
  end

  it "renders attributes in <p>" do
    render
    expect(rendered).to match(/Name/)
    expect(rendered).to match(/Comments/)
    expect(rendered).to match(/Customdian/)
    expect(rendered).to match(/Validation/)
    expect(rendered).to match(/Keywords/)
    expect(rendered).to match(/Full Sample/)
    expect(rendered).to match(/Status/)
    expect(rendered).to match(/MyText/)
    expect(rendered).to match(/Committee/)
    expect(rendered).to match(/false/)
    expect(rendered).to match(/MyText/)
  end
end
