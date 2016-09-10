require 'rails_helper'

RSpec.describe "examples/index", type: :view do
  before(:each) do
    assign(:examples, [
      Example.create!(
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
      ),
      Example.create!(
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
      )
    ])
  end

  it "renders a list of examples" do
    render
    assert_select "tr>td", :text => "Name".to_s, :count => 2
    assert_select "tr>td", :text => "Comments".to_s, :count => 2
    assert_select "tr>td", :text => "Customdian".to_s, :count => 2
    assert_select "tr>td", :text => "Validation".to_s, :count => 2
    assert_select "tr>td", :text => "Keywords".to_s, :count => 2
    assert_select "tr>td", :text => "Full Sample".to_s, :count => 2
    assert_select "tr>td", :text => "Status".to_s, :count => 2
    assert_select "tr>td", :text => "MyText".to_s, :count => 2
    assert_select "tr>td", :text => "Committee".to_s, :count => 2
    assert_select "tr>td", :text => false.to_s, :count => 2
    assert_select "tr>td", :text => "MyText".to_s, :count => 2
  end
end
