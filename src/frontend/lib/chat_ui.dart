import 'package:dash_chat_2/dash_chat_2.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ChatApp extends StatefulWidget {
  const ChatApp({super.key});

  @override
  State<ChatApp> createState() => _ChatAppState();
}

class _ChatAppState extends State<ChatApp> {
  Future<void> getChatResponse(ChatMessage m) async {
    setState(() {
      _messages.insert(0, m);
    });
    final postURL = Uri.parse(url);
    print('URL: $url');
    final response = await http.post(
      postURL,
      body: jsonEncode({'prompt': m.text}),
    );
    if (response.statusCode == 200) {
      print("Response from testing $response and mText is ${m.text}");
      final data = jsonDecode(response.body);
      final botReply = data['AI Result'];
      final ChatMessage reply = ChatMessage(
        user: _bot,
        createdAt: DateTime.now(),
        text: botReply,
      );
      setState(() {
        _messages.insert(0, reply);
      });
    } else {}
  }

  final ChatUser _bot = ChatUser(
    id: '1',
    firstName: "AI",
    lastName: "Assistant",
  );
  final ChatUser _currentUser = ChatUser(id: '2', firstName: "Shidhin");
  List<ChatMessage> _messages = <ChatMessage>[];
  TextEditingController _urlController = TextEditingController();
  String url = "";
  final warningMessageofURL = SnackBar(
    content: Text("Please attach the url"),
    duration: Duration(seconds: 1),
  );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(),
      floatingActionButton: FloatingActionButton.small(
        onPressed: () {
          showDialog(
            barrierDismissible: false,
            context: context,
            builder: (context) {
              return AlertDialog(
                title: Text("Enter Your URL"),
                content: TextField(controller: _urlController),
                actions: [
                  TextButton(
                    onPressed: () {
                      url = _urlController.text;
                      _urlController.clear();
                      Navigator.of(context).pop();
                    },
                    child: Text("Attach"),
                  ),
                  TextButton(
                    onPressed: () {
                      Navigator.pop(context);
                    },
                    child: Text("Decline"),
                  ),
                ],
              );
            },
          );
        },
        child: Icon(Icons.link),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.endTop,
      body: DashChat(
        currentUser: _currentUser,
        onSend: (ChatMessage m) {
          url != ""
              ? getChatResponse(m)
              : ScaffoldMessenger.of(context).showSnackBar(warningMessageofURL);
        },
        messages: _messages,
        inputOptions: InputOptions(
          textInputAction: TextInputAction.send,
          sendOnEnter: true,
        ),
      ),
    );
  }
}
