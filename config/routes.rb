Rails.application.routes.draw do
  resources :examples, only: [:index, :show]
  resources :sections, only: [:index, :show]

  # You can have the root of your site routed with "root"
  root 'sections#index'

end
