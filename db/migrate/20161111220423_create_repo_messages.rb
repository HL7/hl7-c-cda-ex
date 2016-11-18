class CreateRepoMessages < ActiveRecord::Migration
  def change
    create_table :repo_messages do |t|
      t.string  :description
      t.string  :action
      t.text    :body

      t.timestamps null: false
    end
  end
end
