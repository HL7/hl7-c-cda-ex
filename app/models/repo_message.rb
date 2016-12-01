class RepoMessage < ActiveRecord::Base

  def self.build_from_commit_message(action, status, head_commit, source)
    add_list = pull_list(head_commit, 'added')
    add_list_status = init_statuses(add_list)
    mod_list = pull_list(head_commit, 'modified')
    mod_list_status = init_statuses(mod_list)

    RepoMessage.new(action: action, status: status,
                    description: head_commit.include?('message') ? head_commit['message'] : nil,
                    body: head_commit.to_s, new: add_list, new_status: add_list_status,
                    modified: mod_list, modified_status: mod_list_status,
                    repo_source: source)
  end

  private
  def self.pull_list(json_struct, list_tag)
    if json_struct.include?(list_tag) && json_struct[list_tag]
      (json_struct[list_tag].delete_if { |x| !x.include?('/') }).compact
    else
      nil
    end
  end

  def self.init_statuses(list)
    if list
      stat_list = []
      (1..list.count).each { stat_list << 'recd' }
      stat_list
    else
      nil
    end
  end
end
