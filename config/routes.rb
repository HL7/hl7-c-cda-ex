Rails.application.routes.draw do
  namespace :api do
    resources :repository, only: [:create]
  end

  resources :examples, only: [:index, :show]
  resources :sections, only: [:index, :show]

  # You can have the root of your site routed with "root"
  root 'sections#index'

end
