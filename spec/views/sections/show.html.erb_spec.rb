require 'rails_helper'

RSpec.describe 'sections/show', type: :view do
  before(:each) do
    @section = assign(:section, FactoryGirl.create(:section))
  end

  it 'renders attributes in <p>' do
    render
    expect(rendered).to match(/Bacon ipsum dolor amet kielbasa elit landjaeger, pastrami bacon fugiat pig chuck biltong frankfurter ground round ut meatball aute laborum. Deserunt pork chop voluptate swine, pariatur strip steak pork loin sed commodo hamburger spare ribs dolore ribeye est qui. Culpa cillum anim alcatra ipsum tail flank kielbasa aute cupidatat duis occaecat corned beef. Ut exercitation chicken ground round hamburger nulla. Ullamco ex consectetur pork chop boudin do. Meatball laboris leberkas pig. Leberkas sausage do beef ribs cillum doner biltong./)
  end
end
