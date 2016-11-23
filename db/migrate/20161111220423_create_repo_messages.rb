class CreateRepoMessages < ActiveRecord::Migration
  def change
    create_table :repo_messages do |t|
      t.string  :description
      t.string  :action
      t.text    :body
      t.string  :status, limit: 8
      t.string  :new, array: true
      t.string  :new_status, array: true
      t.string  :changed, array: true
      t.string  :changed_status, array: true

      t.timestamps null: false
    end
  end
end
