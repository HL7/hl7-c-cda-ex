class CreateRepoMessages < ActiveRecord::Migration
  def change
    create_table :repo_messages do |t|
      t.string  :description
      t.string  :action
      t.text    :body
      t.string  :status, limit: 8, null: false
      t.string  :repo_source
      t.string  :new, array: true
      t.string  :new_status, array: true
      t.string  :modified, array: true
      t.string  :modified_status, array: true

      t.timestamps null: false
    end
  end
end
