FactoryGirl.define do
  factory :example do
    name       'The-Example'
    comments   'Comment-comment'
    custodian  'Joe Dogg'
    validation 'http://google.com'
    keywords   'dog canine'
    full_sample 'MyString'
    status     'approved'
    example    'MyText'
  end

  factory :approval do
    committee 'Task Force'
    approved  false
  end
end
