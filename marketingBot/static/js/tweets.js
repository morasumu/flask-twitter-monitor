var _dataTable;

$(function() {
  console.log('[Script][Loaded] API Apps');

  initDataTable();

  $('#website-form').submit(function(e) {
    e.preventDefault();
    if (!confirm('Are you sure to submit?')) return false;
    const is_form_valid = validateForm();

    const data = composeFormData();

    const bot_id = Number($('#bot-id').val());
    const promise = bot_id === -1 ? addBotRequest1(data) : updateBotRequest1(bot_id, data);

    return promise.then((res) => {
      if (res.status) {
        toastr.success(res.message);
        refreshTable();
        emptyForm();
      } else {
        toastr.error(res.message);
      }
    })
    .catch((error) => {
      console.log('[Error]', error);
      toastr.error(error.message);
    });
  });

  // deprecated.
  // submit action in the item form.
  $('#website-form1').submit(function(e) {
    e.preventDefault();
    if (!confirm('Are you sure to submit?')) return false;
    const formData = {
      name: $('#name').val(),
      targets: $('#targets').val().split(',').filter((it) => !!it.trim()),
      api_keys: $('#api_keys').val(),
      inclusion_keywords: $('#inclusion_keywords').val().split(',').filter(it => it.trim()),
      exclusion_keywords: $('#exclusion_keywords').val().split(',').filter(it => it.trim()),
      interval: $('#interval').val(),
    };

    const id = Number($('#bot-id').val());

    console.log('[Testing values]', id, formData);

    const promise = id === -1 ? addBotRequest(formData) : updateBotRequest(id, formData);
    return promise.then((res) => {
      if (res.status) {
        toastr.success(res.message);
        refreshTable();
        emptyForm();
      } else {
        toastr.error(res.message);
      }
    })
    .catch((error) => {
      console.log('[Error]', error);
      toastr.error(error.message);
    })
  });
});

function onEdit(id) {
  return getApiAppByIdRequest(id).then((res) => {
    if (res.status) {
      const { data: app } = res;
      $('#bot-id').val(app.id);
      $('#name').val(app.name);
      $('#targets').val(app.targets.join(','));
      $('#api_keys').val(app.api_keys).trigger('change');
      $('#inclusion_keywords').val(app.inclusion_keywords.join(','));
      $('#exclusion_keywords').val(app.exclusion_keywords.join(','));
      $('#interval').val(app.period);

      $('#website-form button[type="submit"]').html('<i class="la la-save"></i>Update');
      $('#form-wrapper').removeClass('_hide').addClass('_show');
      $('#type').val(app.type);
      $('#start_time').val(app.start_time);
      $('#end_time').val(app.end_time);

      addMetricFilter(app.metrics);

    } else {
      toastr.error(res.message);
    }    
  })
  .catch((error) => {
    console.log('[Error]', error);
  })
}

function onDelete(id) {
  if (!confirm('Are you sure proceed to delete?')) return false;
  return deleteTweetByIdRequest(id).then((res) => {
    if (res.status) {
      toastr.success(res.message);
      refreshTable();
    } else {
      toastr.error(res.message);
    }
  })
  .catch((error) => {
    console.log('[Delete]', error);
    toastr.error(error.message);
  })
}

/// --------------- Scripts for UI Operation Events

function validateForm() {
  return true;
}

function composeFormData() {
  const data = new FormData();
  
  data.append('id', $('#bot-id').val())
  data.append('name', $('#name').val());
  data.append('type', $('#type').val());
  data.append('interval', $('#interval').val());
  data.append('api_keys', $('#api_keys').val());
  data.append('start_time', $('#start_time').val());
  data.append('end_time', $('#end_time').val());

  const metricKeys = [];
  const metricValues = [];
  const metrics = {};
  $('.select-metric').each((i, item) => metricKeys.push(item.value));
  $('.min-metric').each((i, item) => metricValues.push(item.value));
  metricKeys.forEach((key, i) => {
    metrics[metricKeys[i]] = metricValues[i];
  });
  data.append('metrics', JSON.stringify(metrics));

  const ids = ['targets', 'inclusion_keywords', 'exclusion_keywords'];
  ids.forEach((id, i) => {
    data.append(id, $(`#${id}_file`).prop('files')[0] || $(`#${id}`).val());
  })

  return data;
}


// ------------------- Scripts for API requests

function initDataTable() {
  // Initialize datatable with ability to add rows dynamically
  var initTableWithDynamicRows = function() {
      _dataTable = $('#tableWithDynamicRows');

      var settings = {
          responsive: true,
          //== DOM Layout settings
          // dom: `<'row'<'col-sm-12'tr>>
          // <'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7 dataTables_pager'lp>>`,

          lengthMenu: [5, 10, 25, 50],

          pageLength: 10,

          language: {
              'lengthMenu': 'Display _MENU_',
          },
          order: [
              [ 0, "asc" ]
          ],
          searching: true,

          processing: true,

          paginate: true,

          serverSide: true,

          ajax: {
              url: "/load-tweets",
              data: function(extra) {
                  extra.keyword = 'test';
              },
              type: 'POST',
              dataSrc: 'data'
          },

          columnDefs: [
              {
                  targets: -1,
                  orderable: false,
                  render: function(obj, type, full, meta) {
                    const data = obj.id;
                    const tweet_id = obj.tweet_id;
                    const tweet_link = `https://twitter.com/${full[2]}/status/${tweet_id}`;
                    return `
                    <a class="edit-row m-portlet__nav-link btn m-btn m-btn--hover-brand m-btn--icon m-btn--icon-only m-btn--pill" title="Open Tweet"
                        href="${tweet_link}" target="_blank">
                      <i class="la la-external-link-square"></i>
                    </a>
                    <span class="edit-row m-portlet__nav-link btn m-btn m-btn--hover-brand m-btn--icon m-btn--icon-only m-btn--pill" title="Edit"
                        onclick="onEdit(${data})"
                        data-domain="${data}">
                      <i class="la la-edit"></i>
                    </span>
                    <span href="#" class="delete-row m-portlet__nav-link btn m-btn m-btn--hover-brand m-btn--icon m-btn--icon-only m-btn--pill" title="Remove"
                      onclick="onDelete(${data})"
                      data-domain="${data}">
                      <i class="la la-trash"></i>
                    </span>`;
                  },
              },
              {
                targets: -3,
                render: function (data, type, full, meta) {
                  data = data.toString()
                    const status = {
                        'true': {'title': 'True', 'class': 'm-badge--success'},
                        'false': {'title': 'False', 'class': 'm-badge--danger'},
                    };
                    data = data.toString();
                    if (typeof status[data] === 'undefined') {
                        return data;
                    }
                    return '<span class="m-badge ' + status[data].class + ' m-badge--wide">' + status[data].title + '</span>';
                },
              },
              // {
              //   targets: 2,
              //   render: function (data, type, full, meta) {
              //     const status = {
              //         'ONE_TIME': {'title': 'One Time', 'class': 'm-badge--info'},
              //         'REAL_TIME': {'title': 'Real Time', 'class': 'm-badge--success'},
              //     };
              //     if (typeof status[data] === 'undefined') {
              //         return data;
              //     }
              //     return '<span class="m-badge ' + status[data].class + ' m-badge--wide">' + status[data].title + '</span>';
              // },
              // },
              // {
              //     targets: 3,
              //     render: function(data, type, full, meta) {
              //       if (data.length) return data.join(',');
              //       return `<span class="m-badge m-badge--warning m-badge--wide">No Targets</span>`;
              //     },
              // },
              // {
              //     targets: 4,
              //     render: function(data, type, full, meta) {
              //       if (full[2] === 'REAL_TIME') return data[0];
              //       return `${data[1]}-${data[2]}`;
              //     },
              // },
              // {
              //   targets: 5,
              //   render: function(data, type, full, meta) {
              //     if (!data.length) {
              //       return `<span class="m-badge m-badge--danger m-badge--wide">None</span>`
              //     }
              //     const names = data.map((api_key) => api_key.name);
              //     return names.join(',');
              //   },
            // },
          ]
      };

      _dataTable.dataTable(settings);
  }
  initTableWithDynamicRows();
}

function updateBotRequest(id, data) {
  return $.ajax({
    url: `/api/bots/${id}`,
    method: 'put',
    data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

function updateBotRequest1(id, data) {
  return $.ajax({
    url : `/api/bot_form/${id}`,
    type : 'PUT',
    data : data,
    processData: false,  // tell jQuery not to process the data
    contentType: false,  // tell jQuery not to set contentType
  });
}

function addBotRequest(data) {
  return $.ajax({
    url: '/api/bots',
    method: 'POST',
    data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
  // return $.ajax({
  //   url: url,
  //   method: 'post',
  //   data: JSON.stringify(data),
  //   contentType: "application/json; charset=utf-8",
  //   dataType: "json"
  // });
}

function addBotRequest1(data) {
  return $.ajax({
    url : 'api/bot_form',
    type : 'POST',
    data : data,
    processData: false,  // tell jQuery not to process the data
    contentType: false,  // tell jQuery not to set contentType
  });
}

function getApiAppByIdRequest(id) {
  return $.ajax({
    url: `/api/bots/${id}`,
    method: 'GET',
    // data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

function deleteTweetByIdRequest(id) {
  return $.ajax({
    url: `/api/tweets/${id}`,
    method: 'DELETE',
    // data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
  });
}

// Scripts for minority

function emptyForm() {
  $('#website-form').find("input[type=text], input[type=hidden], textarea").val("");
  $('#bot-id').val("-1");
  $('#website-form button[type="submit"]').html('<i class="la la-plus"></i>Add');
  $('#form-wrapper').addClass('_hide').removeClass('_show');
  $('#filters').html('');
}

function refreshTable() {
  _dataTable.api().ajax.reload();
}