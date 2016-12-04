FactoryGirl.define do
  factory :example do
    name       'The-Example'
    comments   'Comment-comment'
    custodian  'Joe Dogg'
    validation 'http://google.com'
    keywords   'dog canine'
    full_sample 'MyString'
    status     'app'
    example    'MyText'
    example_url 'http://github.com'

    factory :example_search_1 do
      name      'Allergy'
      comments  'This is breakfast'
      keywords  'bacon'
      custodian "John D'Amore"
      status    'app'
    end

    factory :example_search_2 do
      name      'Allergy to Epinephrine'
      comments  'This is lunch and has eggs'
      keywords  'bacon pork ham'
      custodian 'Cecilia Dogg'
      status    'pend'
    end

    factory :example_search_3 do
      name      'Medication'
      comments  'This is supper'
      keywords  'pork ribeye custard'
      status    'wthd'
    end
  end

  factory :approval do
    committee 'Task Force'
    approved  false
  end
end
